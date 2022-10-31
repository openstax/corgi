from datetime import datetime
from typing import Awaitable, Callable, List
from urllib.parse import parse_qs

from app.core.auth import get_user_role
from app.core.config import CLIENT_ID, CLIENT_SECRET, IS_DEV_ENV
from app.data_models.models import UserSession
from app.github.models import GitHubRepo
from app.github.client import AuthenticatedClient, authenticate_client
from httpx import AsyncClient
from lxml import etree
from sqlalchemy.orm import Session


class AccessDeniedException(BaseException):
    pass


class AuthenticationException(BaseException):
    pass



class GraphQLException(BaseException):
    pass


async def graphql(client: AuthenticatedClient, query: str):
    response = await client.post(
        "https://api.github.com/graphql", json={"query": query})
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:
        raise GraphQLException("\n".join(f'{i + 1}. {e["message"]}'
                               for i, e in enumerate(payload["errors"])))
    return payload


async def get_book_commit_metadata(client: AuthenticatedClient, repo_name: str,
                                   repo_owner: str, version: str):
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
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
    commit = payload["data"]["repository"]["object"]
    commit_sha = commit["oid"]
    commit_timestamp = commit["committedDate"]
    fixed_timestamp = f"{commit_timestamp[:-1]}+00:00"
    books_xml = commit["file"]["object"]["text"]
    meta = etree.fromstring(books_xml, parser=None)

    books = [{ k: el.attrib[k] for k in ("slug", "style") } 
             for el in meta.xpath("//*[local-name()='book']")]
    return (commit_sha, datetime.fromisoformat(fixed_timestamp), books)


async def get_collections(client: AuthenticatedClient, repo_name: str,
                          repo_owner: str, commit_sha: str):
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
    return { entry["name"]: entry["object"]["text"]
            for entry in files_entries }


async def get_user_repositories(
    client: AuthenticatedClient,
    search_query: str
) -> List[GitHubRepo]:
    query_args = {
        "query": f'"{search_query}"',
        "first": "100",
        "type": "REPOSITORY"
    }
    query = '''
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
    '''
    repos = []
    has_next = True
    while has_next:
        # response = await graphql(client, )
        response = await client.post(
            "https://api.github.com/graphql",
            json={
                "query": query.format(query_args=','.join(':'.join(i) 
                                        for i in query_args.items()))
            }
        )
        response.raise_for_status()
        payload = response.json()

        repos.extend([
            GitHubRepo.from_node(node["node"])
            for node in payload["data"]["search"]["edges"]
        ])
        page_info = payload["data"]["search"]["pageInfo"]
        has_next = page_info["hasNextPage"]
        query_args["after"] = f'"{page_info["endCursor"]}"'
    return repos


async def authenticate_user(db: Session, code: str, on_success: Callable[
    [AuthenticatedClient, Session, UserSession], Awaitable[None]]
) -> UserSession:
    async with AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token?"
            f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={code}"
        )
        response.raise_for_status()
        values = parse_qs(response.text)
        if ("access_token" not in values):
            raise AuthenticationException("Could not authenticate")
        
        token = values["access_token"][0]
        client = authenticate_client(client, token)
        user = await get_user(client, token)
        await on_success(client, db, user)
    return user


async def get_user_teams(client: AuthenticatedClient, user: str):
    if IS_DEV_ENV:
        return ['ce-tech']
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


async def get_user(client: AuthenticatedClient, token: str):
    response = await client.get(f"https://api.github.com/user")
    response.raise_for_status()
    json = response.json()
    name = json["login"]
    avatar_url = json["avatar_url"]
    id_ = json["id"]
    user_teams = await get_user_teams(client, name)
    role = get_user_role(user_teams)
    if role is None:
        raise AccessDeniedException("Bad role")
    return UserSession(
        id=id_,
        token=token,
        role=role,
        avatar_url=avatar_url,
        name=name
    )


async def get_repository(client: AuthenticatedClient, repo_name: str,
                         repo_owner: str) -> GitHubRepo:
    query = f"""
        query {{
            repository(name: "{repo_name}", owner: "{repo_owner}") {{
                name
                databaseId
                viewerPermission
            }}
        }}
    """
    payload = await graphql(client, query)
    return GitHubRepo.from_node(payload["data"]["repository"])

