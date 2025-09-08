"""add ancillaries consumer

Revision ID: a853887ac719
Revises: aa75305665c6
Create Date: 2025-09-03 19:22:17.308206

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a853887ac719"
down_revision = "aa75305665c6"
branch_labels = None
depends_on = None


utcnow = datetime.now(timezone.utc)
consumer_table = sa.table(
    "consumer",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
)
approved_book_table = sa.table(
    "approved_book",
    sa.column("book_id", sa.Integer()),
    sa.column("consumer_id", sa.Integer()),
    sa.column("code_version_id", sa.Integer()),
    sa.column("created_at", sa.DateTime()),
    sa.column("updated_at", sa.DateTime()),
)


new_consumers = [
    {"id": 2, "name": "ancillaries", "created_at": utcnow, "updated_at": utcnow}
]


def upgrade():
    bind = op.get_bind()
    insert = consumer_table.insert().values(new_consumers)
    bind.execute(insert)


def downgrade():
    bind = op.get_bind()
    new_consumer_ids = {c["id"] for c in new_consumers}
    delete_abl_entries = approved_book_table.delete().where(
        approved_book_table.c.consumer_id.in_(new_consumer_ids)
    )
    bind.execute(delete_abl_entries)
    delete = consumer_table.delete().where(
        consumer_table.c.id.in_(new_consumer_ids)
    )
    bind.execute(delete)
