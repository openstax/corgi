"""add style column to jobs table

Revision ID: 6b83ef5cce00
Revises: 87653800ea49
Create Date: 2019-12-16 21:33:46.936921

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6b83ef5cce00"
down_revision = "87653800ea49"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("jobs", sa.Column("style", sa.String(), nullable=True))


def downgrade():
    op.drop_column("jobs", "style")
