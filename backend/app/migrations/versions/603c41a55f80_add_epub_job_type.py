"""add epub job type

Revision ID: 603c41a55f80
Revises: 0fb115ce73c2
Create Date: 2023-02-07 19:34:05.500073

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "603c41a55f80"
down_revision = "0fb115ce73c2"
branch_labels = None
depends_on = None


job_types_table = sa.table(
    "job_types",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("display_name", sa.String),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)

jobs_table = sa.table("jobs", sa.column("job_type_id"))
epub_type_id = 6


def upgrade():
    utcnow = datetime.now(timezone.utc)
    server_data = [
        {
            "id": epub_type_id,
            "name": "git-epub",
            "display_name": "EPUB (git)",
            "created_at": utcnow,
            "updated_at": utcnow,
        }
    ]

    bind = op.get_bind()
    insert = job_types_table.insert().values(server_data)
    bind.execute(insert)


def downgrade():
    bind = op.get_bind()
    delete_jobs_of_seeded_type = jobs_table.delete().where(
        jobs_table.c.job_type_id.in_([epub_type_id])
    )
    delete_seed = job_types_table.delete().where(
        job_types_table.c.id.in_([epub_type_id])
    )
    bind.execute(delete_jobs_of_seeded_type)
    bind.execute(delete_seed)
