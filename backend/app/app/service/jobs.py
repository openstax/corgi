from app.db.schema import Jobs as JobsSchema
from app.data_models.models import Jobs as JobsModel
from app.service.base import ServiceBase


class JobsService(ServiceBase):
    """If specific methods need to be overridden they can be done here.
    """
    pass


jobs_service = JobsService(JobsSchema, JobsModel)
