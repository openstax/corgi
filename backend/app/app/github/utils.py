from app.data_models.models import UserSession
from app.db.schema import Repository
from app.github.api import get_user_repositories
from app.github.client import AuthenticatedClient
from app.service.repository import repository_service
from app.service.user import user_service
from sqlalchemy.orm import Session


async def sync_user_data(client: AuthenticatedClient,
                         db: Session, user: UserSession):
    """A utility function to fetch and store user data"""

    user_repos = await get_user_repositories(
        client, "org:openstax osbooks in:name")
    user_repos = [ur for ur in user_repos if ur.name.startswith("osbooks-")]
    user_service.upsert_user(db, user)
    repository_service.upsert_repositories(db, [
        Repository(id=repo.database_id, name=repo.name, owner="openstax")
        for repo in user_repos
    ])
    repository_service.upsert_user_repositories(db, user.id, user_repos)

