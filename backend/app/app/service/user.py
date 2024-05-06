from typing import List

from sqlalchemy.orm import Session

from app.data_models.models import User as UserModel
from app.data_models.models import UserSession
from app.db.schema import Repository as RepositorySchema
from app.db.schema import User as UserSchema
from app.db.schema import UserRepository
from app.github import GitHubRepo, RepositoryPermission
from app.service.base import ServiceBase


class UserService(ServiceBase):
    def get_user_repositories(
        self, db: Session, user: UserSession
    ) -> List[RepositorySchema]:
        query = db.query(UserRepository).filter(
            UserRepository.user_id == user.id
        )
        return [ur.repository for ur in query.all()]

    def upsert_user_repositories(
        self, db: Session, user: UserSession, repositories: List[GitHubRepo]
    ):
        for repo in repositories:
            permission_id = RepositoryPermission[repo.viewer_permission]
            db.merge(
                UserRepository(
                    user_id=user.id,
                    permission_id=permission_id,
                    repository_id=repo.database_id,
                )
            )
        db.commit()

    def upsert_user(self, db: Session, user: UserSession):
        db.merge(
            UserSchema(id=user.id, name=user.name, avatar_url=user.avatar_url)
        )
        db.commit()


user_service = UserService(UserSchema, UserModel)
