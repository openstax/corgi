from typing import List
from enum import Enum

from app.db.schema import (Repository, User, UserRepository,
                           RepositoryPermission)
from app.service.base import ServiceBase
from app.data_models.models import GitHubRepo
from app.auth.utils import AuthenticatedClient, UserSession
from sqlalchemy.orm import Session as BaseSession


class RepositoryPermission(int, Enum):
    ADMIN = 1
    MAINTAIN = 2
    READ = 3
    TRIAGE = 4
    WRITE = 5


class RepositoryService:
    async def get_user_repositories(
        self,
        client: AuthenticatedClient,
        search_query: str = "org:openstax osbooks in:name archived:false"
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

    def upsert_repositories(self, db: BaseSession, 
                            repositories: List[Repository]):
        for repo in repositories:
            db.merge(repo)
        db.commit()
    
    def upsert_user_repositories(self, db: BaseSession, user_id: int, 
                                 repo_list: List[GitHubRepo]):
        for repo in repo_list:
            permission_id = RepositoryPermission[repo.viewer_permission]
            db.merge(UserRepository(user_id=user_id, 
                                    permission_id=permission_id,
                                    repository_id=repo.database_id))
        db.commit()


class UserService:
    def upsert_user(self, db: BaseSession, user: UserSession):
        db.merge(User(id=user.id, name=user.name, avatar_url=user.avatar_url))
        db.commit()


user_service = UserService()
repository_service = RepositoryService()
