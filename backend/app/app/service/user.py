from app.service.base import ServiceBase
from app.data_models.models import UserSession
from app.data_models.models import User as UserModel
from app.db.schema import User as UserSchema
from sqlalchemy.orm import Session


class UserService(ServiceBase):
    def upsert_user(self, db: Session, user: UserSession):
        db.merge(UserSchema(id=user.id, name=user.name, avatar_url=user.avatar_url))
        db.commit()


user_service = UserService(UserSchema, UserModel)