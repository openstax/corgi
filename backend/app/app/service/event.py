from app.db.schema import Events as EventsSchema
from app.data_models.models import Event as EventModel
from app.service.base import ServiceBase


class EventsService(ServiceBase):
    """If specific methods need to be overridden they can be done here.
    """
    pass

event_service = EventsService(EventsSchema, EventModel)
