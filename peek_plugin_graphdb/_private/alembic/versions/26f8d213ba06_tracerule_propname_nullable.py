"""tracerule.propname nullable

Peek Plugin Database Migration Script

Revision ID: 26f8d213ba06
Revises: 6dac32ecea20
Create Date: 2019-08-12 20:24:41.256117

"""

# revision identifiers, used by Alembic.
revision = "26f8d213ba06"
down_revision = "6dac32ecea20"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "GraphDbTraceConfigRule",
        "propertyName",
        existing_type=sa.VARCHAR(),
        nullable=True,
        schema="pl_graphdb",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "GraphDbTraceConfigRule",
        "propertyName",
        existing_type=sa.VARCHAR(),
        nullable=False,
        schema="pl_graphdb",
    )
    # ### end Alembic commands ###
