from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.core.auth import get_user_role
from app.core.config import IS_DEV_ENV
from app.core.errors import CustomBaseError
from app.data_models.models import UserSession
from app.github.client import AuthenticatedClient
from app.github.models import GitHubRepo
from lxml import etree


class AccessDeniedError(CustomBaseError):
    pass


class GraphQLError(CustomBaseError):
    pass


async def graphql(client: AuthenticatedClient, query: str):
    response = await client.post(
        "https://api.github.com/graphql", json={"query": query})
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:  # pragma: no cover
        raise GraphQLError(", ".join(e["message"]
                               for e in payload["errors"]))
    return payload


async def get_book_repository(
        client: AuthenticatedClient,
        repo_name: str,
        repo_owner: str,
        version: str) -> Tuple[GitHubRepo, str, datetime, List[Dict[str, Any]]]:
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
                databaseId
                viewerPermission
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
    repo = GitHubRepo(name=repo_name,
                      database_id=repository["databaseId"],
                      viewer_permission=repository["viewerPermission"])
    commit = repository["object"]
    commit_sha = commit["oid"]
    commit_timestamp = commit["committedDate"]
    fixed_timestamp = f"{commit_timestamp[:-1]}+00:00"
    books_xml = commit["file"]["object"]["text"]
    meta = etree.fromstring(books_xml, parser=None)

    books = [{k: el.attrib[k] for k in ("slug", "style")}
             for el in meta.xpath("//*[local-name()='book']")]
    return (repo, commit_sha, datetime.fromisoformat(fixed_timestamp), books)


async def get_collections(
        client: AuthenticatedClient,
        repo_name: str,
        repo_owner: str,
        commit_sha: str) -> Dict[str, str]:
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
    files_entries = (payload["data"]["repository"]["object"]["file"]["object"]
                     ["entries"])
    return {entry["name"]: entry["object"]["text"]
            for entry in files_entries}


async def get_user_repositories(
        client: AuthenticatedClient,
        search_query: str) -> List[GitHubRepo]:
    query_args = {
        "query": f'"{search_query}"',
        "first": "100",
        "type": "REPOSITORY"
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
                            name
                            databaseId
                            viewerPermission
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
                    query_args=','.join(
                        ':'.join(i) for i in query_args.items()))}
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
                organization(login: "openstax") {{
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
        id=id_,
        token=token,
        role=role,
        avatar_url=avatar_url,
        name=name
    )
