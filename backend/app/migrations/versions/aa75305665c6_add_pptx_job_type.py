"""add pptx job type

Revision ID: aa75305665c6
Revises: 3e801ba4d7e0
Create Date: 2024-07-24 20:53:20.517446

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "aa75305665c6"
down_revision = "3e801ba4d7e0"
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


def upgrade():
    utcnow = datetime.now(timezone.utc)
    server_data = [
        {
            "id": 7,
            "name": "git-pptx",
            "display_name": "PPTX (git)",
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
        jobs_table.c.job_type_id.in_([7])
    )
    delete_seed = job_types_table.delete().where(job_types_table.c.id.in_([7]))
    bind.execute(delete_jobs_of_seeded_type)
    bind.execute(delete_seed)
