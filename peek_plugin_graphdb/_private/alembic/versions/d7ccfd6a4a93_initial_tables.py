"""initial tables

Peek Plugin Database Migration Script

Revision ID: d7ccfd6a4a93
Revises: 
Create Date: 2018-10-12 20:09:58.162336

"""

# revision identifiers, used by Alembic.
revision = 'd7ccfd6a4a93'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('GraphDbModelSet',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('propsJson', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key'),
    sa.UniqueConstraint('name'),
    schema='pl_graphdb'
    )
    op.create_table('Setting',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_graphdb'
    )
    op.create_table('GraphDbChunkQueue',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('modelSetId', sa.Integer(), nullable=False),
    sa.Column('chunkKey', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['modelSetId'], ['pl_graphdb.GraphDbModelSet.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', 'chunkKey'),
    schema='pl_graphdb'
    )
    op.create_table('GraphDbEncodedChunkTuple',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('modelSetId', sa.Integer(), nullable=False),
    sa.Column('chunkKey', sa.String(), nullable=False),
    sa.Column('encodedData', sa.LargeBinary(), nullable=False),
    sa.Column('encodedHash', sa.String(), nullable=False),
    sa.Column('lastUpdate', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['modelSetId'], ['pl_graphdb.GraphDbModelSet.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_graphdb'
    )
    op.create_index('idx_Chunk_modelSetId_chunkKey', 'GraphDbEncodedChunkTuple', ['modelSetId', 'chunkKey'], unique=False, schema='pl_graphdb')
    op.create_table('GraphDbSegment',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('modelSetId', sa.Integer(), nullable=False),
    sa.Column('importGroupHash', sa.String(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('chunkKey', sa.String(), nullable=False),
    sa.Column('segmentJson', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['modelSetId'], ['pl_graphdb.GraphDbModelSet.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_graphdb'
    )
    op.create_index('idx_Segment_gridKey', 'GraphDbSegment', ['chunkKey'], unique=False, schema='pl_graphdb')
    op.create_index('idx_Segment_importGroupHash', 'GraphDbSegment', ['importGroupHash'], unique=False, schema='pl_graphdb')
    op.create_index('idx_Segment_key', 'GraphDbSegment', ['modelSetId', 'key'], unique=True, schema='pl_graphdb')
    op.create_table('GraphDbTraceConfig',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('modelSetId', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('isEnabled', sa.Boolean(), server_default='true', nullable=False),
    sa.ForeignKeyConstraint(['modelSetId'], ['pl_graphdb.GraphDbModelSet.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_graphdb'
    )
    op.create_index('idx_TraceConfig_key', 'GraphDbTraceConfig', ['modelSetId', 'key'], unique=True, schema='pl_graphdb')
    op.create_index('idx_TraceConfig_name', 'GraphDbTraceConfig', ['modelSetId', 'name'], unique=True, schema='pl_graphdb')
    op.create_table('SettingProperty',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('settingId', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('type', sa.String(length=16), nullable=True),
    sa.Column('int_value', sa.Integer(), nullable=True),
    sa.Column('char_value', sa.String(), nullable=True),
    sa.Column('boolean_value', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['settingId'], ['pl_graphdb.Setting.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_graphdb'
    )
    op.create_index('idx_SettingProperty_settingId', 'SettingProperty', ['settingId'], unique=False, schema='pl_graphdb')
    op.create_table('GraphDbTraceConfigRule',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('traceConfigId', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('applyTo', sa.Integer(), nullable=False),
    sa.Column('action', sa.Integer(), nullable=False),
    sa.Column('actionData', sa.String(), nullable=True),
    sa.Column('propertyName', sa.String(), nullable=False),
    sa.Column('propertyValue', sa.String(), nullable=False),
    sa.Column('propertyValueType', sa.Integer(), nullable=False),
    sa.Column('comment', sa.String(), nullable=True),
    sa.Column('isEnabled', sa.Boolean(), server_default='true', nullable=False),
    sa.ForeignKeyConstraint(['traceConfigId'], ['pl_graphdb.GraphDbTraceConfig.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_graphdb'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('GraphDbTraceConfigRule', schema='pl_graphdb')
    op.drop_index('idx_SettingProperty_settingId', table_name='SettingProperty', schema='pl_graphdb')
    op.drop_table('SettingProperty', schema='pl_graphdb')
    op.drop_index('idx_TraceConfig_name', table_name='GraphDbTraceConfig', schema='pl_graphdb')
    op.drop_index('idx_TraceConfig_key', table_name='GraphDbTraceConfig', schema='pl_graphdb')
    op.drop_index('idx_TraceConfig_importGroupHash', table_name='GraphDbTraceConfig', schema='pl_graphdb')
    op.drop_table('GraphDbTraceConfig', schema='pl_graphdb')
    op.drop_index('idx_Segment_key', table_name='GraphDbSegment', schema='pl_graphdb')
    op.drop_index('idx_Segment_importGroupHash', table_name='GraphDbSegment', schema='pl_graphdb')
    op.drop_index('idx_Segment_gridKey', table_name='GraphDbSegment', schema='pl_graphdb')
    op.drop_table('GraphDbSegment', schema='pl_graphdb')
    op.drop_index('idx_Chunk_modelSetId_chunkKey', table_name='GraphDbEncodedChunkTuple', schema='pl_graphdb')
    op.drop_table('GraphDbEncodedChunkTuple', schema='pl_graphdb')
    op.drop_table('GraphDbChunkQueue', schema='pl_graphdb')
    op.drop_table('Setting', schema='pl_graphdb')
    op.drop_table('GraphDbModelSet', schema='pl_graphdb')
    # ### end Alembic commands ###