import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE SETTINGS
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
)
SQLALCHEMY_POOL_SIZE = os.getenv("SQLALCHEMY_POOL_SIZE", 10)
SQLALCHEMY_MAX_OVERFLOW = os.getenv("SQLALCHEMY_MAX_OVERFLOW", 5)

# CORS SETTINGS
# a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200"
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS"
)

# VERSION SETTINGS
REVISION = os.getenv("REVISION")
TAG = os.getenv("TAG")
STACK_NAME = os.getenv("STACK_NAME")
DEPLOYED_AT = os.getenv("DEPLOYED_AT")

# GITHUB SETTINGS
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")

# GITHUB OAUTH
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ADMIN_TEAMS = ("ce-tech", "ce-admins", "content-managers")
GITHUB_LOGIN_URL = (
    "https://github.com/login/oauth/authorize?"
    f"client_id={CLIENT_ID}&scope=read:user%20read:org"
)

# JWT
# tr -dc 'a-zA-Z0-9[:punct:]' < /dev/urandom | dd bs=1000 count=1 2>/dev/null
SESSION_SECRET = (
    "cMzeqhQ2HsM2LFPRJBy43kNdqv9RNEMMxtmk3RmLNN5M1bfhKR4ofgXe8DpzIjUl"
    "DGjPJU0L6webMfMIAz9pWlEPc2CkroTaOuOesASoihqb1J586YxCDjdI7jJ9ZVpB"
    "fvyPPHyVKrnIYFnQDoof2Z9GTR8TIKqt6J2qtQj3QlUWvMj9PyMAh4CJq7lEjCAR"
    "jJqkWY6nG4HAQl5f6WeOYUmNiDEqRvSuwSQhcNjVgoz4vxKQorqni2C5JBvXY0Te"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
