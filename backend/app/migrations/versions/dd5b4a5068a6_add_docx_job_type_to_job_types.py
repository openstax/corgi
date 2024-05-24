"""add docx job type to job types

Revision ID: dd5b4a5068a6
Revises: c242e42f4bc1
Create Date: 2022-07-25 14:38:25.831153

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dd5b4a5068a6"
down_revision = "c242e42f4bc1"
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
            "id": 5,
            "name": "git-docx",
            "display_name": "Docx (git)",
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
        jobs_table.c.job_type_id.in_([5])
    )
    delete_seed = job_types_table.delete().where(job_types_table.c.id.in_([5]))
    bind.execute(delete_jobs_of_seeded_type)
    bind.execute(delete_seed)
