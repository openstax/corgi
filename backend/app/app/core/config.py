import os

# DATABASE SETTINGS
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
SQLALCHEMY_POOL_SIZE = os.getenv("SQLALCHEMY_POOL_SIZE", 10)
SQLALCHEMY_MAX_OVERFLOW = os.getenv("SQLALCHEMY_MAX_OVERFLOW", 5)

# CORS SETTINGS
# a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200"
BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS")

# VERSION SETTINGS
REVISION = os.getenv("REVISION")
TAG = os.getenv("TAG")
STACK_NAME = os.getenv("STACK_NAME")
DEPLOYED_AT = os.getenv("DEPLOYED_AT")

IS_DEV_ENV = STACK_NAME is None or STACK_NAME == "dev"

if IS_DEV_ENV:
    from dotenv import load_dotenv

    load_dotenv()


# GITHUB SETTINGS
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG", "openstax")
GITHUB_REPO_PREFIX = os.getenv("GITHUB_REPO_PREFIX", "osbooks")

# Rex web
REX_WEB_RELEASE_URL = os.getenv(
    "REX_WEB_RELEASE_URL", "https://openstax.org/rex/release.json"
)

# GITHUB OAUTH
CLIENT_ID = os.getenv("GITHUB_OAUTH_ID")
CLIENT_SECRET = os.getenv("GITHUB_OAUTH_SECRET")
ADMIN_TEAMS = ("ce-tech", "ce-admins", "content-managers")

# To encrypt session cookie
SESSION_SECRET = os.getenv("SESSION_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = 480
