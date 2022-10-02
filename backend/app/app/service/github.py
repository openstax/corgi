from typing import List
from enum import Enum

from app.db.schema import (Repository, User, UserRepository, Commit, Book,
                           RepositoryPermission)
from app.service.base import ServiceBase
from app.data_models.models import GitHubRepo
from app.auth.utils import UserSession
from httpx import AsyncClient
from sqlalchemy.orm import Session as BaseSession


class RepositoryPermission(int, Enum):
    ADMIN = 1
    MAINTAIN = 2
    READ = 3
    TRIAGE = 4
    WRITE = 5


class RepositoryService:
    async def get_user_repositories(self, client: AsyncClient) -> List[GitHubRepo]:
        query = """
            query {
                search(
                    query: "org:openstax osbooks in:name archived:false",
                    type: REPOSITORY,
                    first: 100
                ) {
                    repositoryCount
                    edges {
                        node {
                            ... on Repository {
                                name
                                databaseId
                                viewerPermission
                            }
                        }
                    }
                }
            }
        """
        repos = []
        # NOTE: Right now it is assumed that the `client` has the authorization 
        #       header set. It might be better to make a subclass of AsyncClient
        #       that can only be initialized with a token. Using a subclass
        #       would make it more clear when a function/request needs 
        #       authorization
        response = await client.post("https://api.github.com/graphql",
                                        json={"query": query})
        response.raise_for_status()
        payload = response.json()
        # TODO: while repositoryCount == $first, make another request
        repos.extend([
            GitHubRepo.from_node(node["node"])
            for node in payload["data"]["search"]["edges"]
        ])
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
