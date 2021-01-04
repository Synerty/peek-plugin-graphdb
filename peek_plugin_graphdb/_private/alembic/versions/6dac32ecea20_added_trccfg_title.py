"""Added TrcCfg.title

Peek Plugin Database Migration Script

Revision ID: 6dac32ecea20
Revises: bdc665a4d160
Create Date: 2019-06-18 15:14:53.226071

"""

# revision identifiers, used by Alembic.
revision = "6dac32ecea20"
down_revision = "bdc665a4d160"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "GraphDbTraceConfig",
        sa.Column("title", sa.String(), nullable=True),
        schema="pl_graphdb",
    )
    op.execute(""" UPDATE "pl_graphdb"."GraphDbTraceConfig" SET "title" = "name" """)
    op.alter_column(
        "GraphDbTraceConfig",
        "title",
        type_=sa.String(),
        nullable=False,
        schema="pl_graphdb",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("GraphDbTraceConfig", "title", schema="pl_graphdb")
    # ### end Alembic commands ###
