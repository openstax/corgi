from typing import List

from sqlalchemy.orm import Session

from app.data_models.models import Repository as RepositoryModel
from app.db.schema import Repository as RepositorySchema
from app.service.base import ServiceBase


class RepositoryService(ServiceBase):
    def upsert_repositories(
        self, db: Session, repositories: List[RepositorySchema]
    ):
        for repo in repositories:
            db.merge(repo)
        db.commit()


repository_service = RepositoryService(RepositorySchema, RepositoryModel)
