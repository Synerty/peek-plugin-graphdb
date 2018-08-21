import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index, Sequence
from vortex.Tuple import addTupleType, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from .DeclarativeBase import DeclarativeBase
from .GraphDbModelSet import GraphDbModelSet

logger = logging.getLogger(__name__)


@addTupleType
class GraphDbVertex(Tuple, DeclarativeBase):
    __tablename__ = 'GraphDbVertex'
    __tupleType__ = graphDbTuplePrefix + __tablename__

    id_seq = Sequence('GraphDbVertex_id_seq',
                      metadata=DeclarativeBase.metadata,
                      schema=DeclarativeBase.metadata.schema)

    id = Column(Integer, id_seq, server_default=id_seq.next_value(),
                primary_key=True, autoincrement=False)

    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet)

    #: The unique reference for this vertex
    key = Column(String(50), nullable=False)

    #: A unique name for this vertex
    name = Column(String(50), nullable=False)

    #: A description, or long name for this vertex.
    desc = Column(String(200), nullable=True)

    #: Properties associated with this vertex
    propsJson = Column(String)

    __table_args__ = (
        Index("idx_GraphDbVertex_modelSet_key", modelSetId, name, unique=True),
        Index("idx_GraphDbVertex_modelSet_key", modelSetId, key, unique=True),
    )
