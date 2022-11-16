from app.data_models.models import UserSession
from app.db.schema import Repository
from app.github.api import get_user_repositories
from app.github.client import AuthenticatedClient
from app.service.repository import repository_service
from app.service.user import user_service, RepositoryPermission
from sqlalchemy.orm import Session


async def sync_user_data(client: AuthenticatedClient,
                         db: Session, user: UserSession):
    """A utility function to fetch and store user data"""

    user_repos = await get_user_repositories(
        client, "org:openstax osbooks in:name")
    user_repos = [r for r in user_repos if r.name.startswith("osbooks-")]
    if not user.is_admin():
        user_repos = [
            r for r in user_repos if r.viewer_permission in (
                RepositoryPermission.ADMIN.name,
                RepositoryPermission.WRITE.name)]
    user_service.upsert_user(db, user)
    repository_service.upsert_repositories(db, [
        Repository(id=repo.database_id, name=repo.name, owner="openstax")
        for repo in user_repos
    ])
    user_service.upsert_user_repositories(db, user, user_repos)
