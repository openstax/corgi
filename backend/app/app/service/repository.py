from enum import Enum
from typing import List

from app.core.auth import Role
from app.data_models.models import Repository as RepositoryModel
from app.data_models.models import UserSession
from app.db.schema import Repository as RepositorySchema
from app.db.schema import UserRepository
from app.github import GitHubRepo
from app.service.base import ServiceBase
from sqlalchemy.orm import Session


class RepositoryPermission(int, Enum):
    ADMIN = 1
    MAINTAIN = 2
    READ = 3
    TRIAGE = 4
    WRITE = 5


class RepositoryService(ServiceBase):
    def get_user_repositories(
        self,
        db: Session,
        user: UserSession
    ) -> List[RepositoryModel]:
        query = db.query(UserRepository)
        if user.role != Role.ADMIN:
            query = query.filter(
                UserRepository.user_id == user.id,
                UserRepository.permission_id.in_([
                    RepositoryPermission.ADMIN,
                    RepositoryPermission.WRITE
                ])
            )
        else:
            query = query = query.filter(UserRepository.user_id == user.id)
        return [ur.repository for ur in query.all()]

    def upsert_repositories(self, db: Session, 
                            repositories: List[RepositorySchema]):
        for repo in repositories:
            db.merge(repo)
        db.commit()
    
    def upsert_user_repositories(self, db: Session, user_id: int, 
                                 repo_list: List[GitHubRepo]):
        for repo in repo_list:
            permission_id = RepositoryPermission[repo.viewer_permission]
            db.merge(UserRepository(user_id=user_id, 
                                    permission_id=permission_id,
                                    repository_id=repo.database_id))
        db.commit()


repository_service = RepositoryService(RepositorySchema, RepositoryModel)
