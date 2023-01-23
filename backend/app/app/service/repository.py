from typing import List

from app.data_models.models import Repository as RepositoryModel
from app.db.schema import Repository as RepositorySchema
from app.service.base import ServiceBase
from sqlalchemy.orm import Session


class RepositoryService(ServiceBase):
    def upsert_repositories(
            self,
            db: Session,
            repositories: List[RepositorySchema]):
        for repo in repositories:
            db.merge(repo)
        db.commit()


repository_service = RepositoryService(RepositorySchema, RepositoryModel)
