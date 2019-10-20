import os

# DATABASE SETTINGS
PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DBNAME = os.getenv("PG_DBNAME")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DBNAME}"
)

# CORS SETTINGS
# a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200"
BACKEND_CORS_ORIGINS = os.getenv(
    "BACKEND_CORS_ORIGINS"
)
