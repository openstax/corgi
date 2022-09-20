import os

from dotenv import load_dotenv


# tr -dc 'a-zA-Z0-9[:punct:]' < /dev/urandom | dd bs=1000 count=1 2>/dev/null
load_dotenv()
SECRET_KEY = (
    "cMzeqhQ2HsM2LFPRJBy43kNdqv9RNEMMxtmk3RmLNN5M1bfhKR4ofgXe8DpzIjUl"
    "DGjPJU0L6webMfMIAz9pWlEPc2CkroTaOuOesASoihqb1J586YxCDjdI7jJ9ZVpB"
    "fvyPPHyVKrnIYFnQDoof2Z9GTR8TIKqt6J2qtQj3QlUWvMj9PyMAh4CJq7lEjCAR"
    "jJqkWY6nG4HAQl5f6WeOYUmNiDEqRvSuwSQhcNjVgoz4vxKQorqni2C5JBvXY0Te"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
ADMIN_TEAMS = ("ce-tech", "ce-admins", "content-managers")
GITHUB_LOGIN_URL = (
    "https://github.com/login/oauth/authorize?"
    f"client_id={CLIENT_ID}&scope=read:user%20read:org"
)