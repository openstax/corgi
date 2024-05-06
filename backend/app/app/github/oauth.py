from authlib.integrations.starlette_client import OAuth

from app.core.config import CLIENT_ID, CLIENT_SECRET

oauth = OAuth()
oauth.register(
    "github",
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    scope="read:user read:org repo",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
)


if oauth.github is None:  # pragma: no cover
    raise Exception("BUG: GitHub oauth could not be registered")


github_oauth = oauth.github
