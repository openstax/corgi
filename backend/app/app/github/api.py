import base64
import json
from datetime import datetime
from typing import Any, Dict, List, Tuple

from lxml import etree

from app.core.auth import get_user_role
from app.core.config import GITHUB_ORG, IS_DEV_ENV
from app.core.errors import CustomBaseError
from app.data_models.models import UserSession
from app.github.client import AuthenticatedClient
from app.github.models import GitHubRepo
from app.xml_utils import get_attr, parse_xml_doc, xpath_some


class AccessDeniedError(CustomBaseError):
    pass


class GraphQLError(CustomBaseError):
    pass


async def graphql(client: AuthenticatedClient, query: str):
    response = await client.post(
        "https://api.github.com/graphql", json={"query": query}
    )
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:  # pragma: no cover
        raise GraphQLError(", ".join(e["message"] for e in payload["errors"]))
    return payload


async def get_book_repository(
    client: AuthenticatedClient, repo_name: str, repo_owner: str, version: str
) -> Tuple[GitHubRepo, str, datetime, List[Dict[str, Any]]]:
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
                {GitHubRepo.graphql_query()}
                object(expression: "{version}") {{
                    oid
                    ... on Commit {{
                        committedDate
                        file (path: "META-INF/books.xml") {{
                            object {{
                                ... on Blob {{
                                    text
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    payload = await graphql(client, query)
    repository = payload["data"]["repository"]
    repo = GitHubRepo.from_node(repository)
    commit = repository["object"]
    if commit is None:  # pragma: no cover
        raise CustomBaseError(f"Could not find commit '{version}'")
    commit_sha = commit["oid"]
    commit_timestamp = commit["committedDate"]
    books_xml = commit["file"]["object"]["text"]
    meta = parse_xml_doc(books_xml)

    books = [
        {k: get_attr(el, k) for k in ("slug", "style")}
        for el in xpath_some(meta, "//*[local-name()='book']")
    ]
    return (repo, commit_sha, datetime.fromisoformat(commit_timestamp), books)


async def get_collections(
    client: AuthenticatedClient,
    repo_name: str,
    repo_owner: str,
    commit_sha: str,
) -> Dict[str, etree.ElementBase]:
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
                object(expression: "{commit_sha}") {{
                    ... on Commit {{
                        file (path: "collections") {{
                            object {{
                                ... on Tree {{
                                    entries {{
                                        name
                                        object {{
                                            ... on Blob {{
                                                text
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    """
    payload = await graphql(client, query)
    files_entries = payload["data"]["repository"]["object"]["file"]["object"][
        "entries"
    ]
    return {
        entry["name"]: parse_xml_doc(entry["object"]["text"])
        for entry in files_entries
    }


async def push_to_github(
    client: AuthenticatedClient,
    path: str,
    content: str,
    owner: str,
    repo: str,
    branch: str,
    commit_message: str,
    file_exists=True,
):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    base64content = base64.b64encode(content.encode("utf-8"))
    message = {
        "message": commit_message,
        "branch": branch,
        "content": base64content.decode("utf-8"),
    }

    if file_exists:
        response = await client.get(url + "?ref=" + branch)
        response.raise_for_status()
        data = response.json()
        message["sha"] = data["sha"]

        if base64content.decode("utf-8").strip() == data["content"].strip():
            raise CustomBaseError("No changes to push")

    response = await client.put(
        url,
        data=json.dumps(message),
        headers={
            **client.headers,
            "Content-Type": "application/json",
        },
    )

    response.raise_for_status()


async def get_user_repositories(
    client: AuthenticatedClient, search_query: str
) -> List[GitHubRepo]:
    query_args = {
        "query": f'"{search_query}"',
        "first": "100",
        "type": "REPOSITORY",
    }
    query = """
        query {{
            search({query_args}) {{
                repositoryCount
                pageInfo {{
                    endCursor
                    hasNextPage
                }}
                edges {{
                    node {{
                        ... on Repository {{
                            {repo_query}
                        }}
                    }}
                }}
            }}
        }}
    """
    repos = []
    has_next = True
    while has_next:
        # response = await graphql(client, )
        response = await client.post(
            "https://api.github.com/graphql",
            json={
                "query": query.format(
                    query_args=",".join(
                        ":".join(i) for i in query_args.items()
                    ),
                    repo_query=GitHubRepo.graphql_query(),
                )
            },
        )
        response.raise_for_status()
        payload = response.json()

        for node in payload["data"]["search"]["edges"]:
            repos.append(GitHubRepo.from_node(node["node"]))

        page_info = payload["data"]["search"]["pageInfo"]
        has_next = page_info["hasNextPage"]
        query_args["after"] = f'"{page_info["endCursor"]}"'
    return repos


async def get_user_teams(client: AuthenticatedClient, user: str) -> List[str]:
    if IS_DEV_ENV:  # pragma: no cover
        return ["ce-tech"]
    else:
        query = f"""
            query {{
                organization(login: "{GITHUB_ORG}") {{
                    teams(first: 100, userLogins: ["{user}"]) {{
                        totalCount
                        edges {{
                            node {{
                                name
                                description
                            }}
                        }}
                    }}
                }}
            }}
        """

        payload = await graphql(client, query)

        return [
            node["node"]["name"]
            for node in payload["data"]["organization"]["teams"]["edges"]
        ]


async def get_user(client: AuthenticatedClient, token: str) -> UserSession:
    response = await client.get("https://api.github.com/user")
    response.raise_for_status()
    json = response.json()
    name = json["login"]
    avatar_url = json["avatar_url"]
    id_ = json["id"]
    user_teams = await get_user_teams(client, name)
    role = get_user_role(user_teams)
    if role is None:
        raise AccessDeniedError("Bad role")
    return UserSession(
        id=id_, token=token, role=role, avatar_url=avatar_url, name=name
    )
