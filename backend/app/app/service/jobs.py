from app.auth.utils import UserSession
from app.db.schema import Jobs as JobSchema
from app.data_models.models import Job as JobModel, JobCreate
from app.service.base import ServiceBase
from sqlalchemy.orm import Session as BaseSession


class JobsService(ServiceBase):
    """If specific methods need to be overridden they can be done here.
    """
    def create(
        self, db_session: BaseSession, job_in: JobCreate, user: UserSession
    ):
        pass


jobs_service = JobsService(JobSchema, JobModel)
