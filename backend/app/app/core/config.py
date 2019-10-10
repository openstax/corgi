import os

# DATABASE SETTINGS
PG_HOST = os.getenv("PG_HOST")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DBNAME = os.getenv("PG_DBNAME")
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DBNAME}"
)
