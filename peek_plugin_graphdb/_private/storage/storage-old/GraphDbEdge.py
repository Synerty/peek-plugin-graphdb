import logging

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Index, Sequence
from vortex.Tuple import addTupleType, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.GraphDbVertex import GraphDbVertex
from .DeclarativeBase import DeclarativeBase
from .GraphDbModelSet import GraphDbModelSet

logger = logging.getLogger(__name__)


@addTupleType
class GraphDbEdge(Tuple, DeclarativeBase):
    __tablename__ = 'GraphDbEdge'
    __tupleType__ = graphDbTuplePrefix + __tablename__

    id_seq = Sequence('GraphDbEdge_id_seq',
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

    #: The unique reference for this segment of the graph
    segmentHash = Column(String(50), nullable=False)

    #: Properties associated with this vertex
    propsJson = Column(String)

    #: A reference to the source node
    srcId = Column(Integer,
                   ForeignKey('GraphDbVertex.id', ondelete='CASCADE'),
                   nullable=False)
    src = relationship(GraphDbVertex,
                       primaryjoin="GraphDbEdge.srcId==GraphDbVertex.id")

    #: A reference to the destination node
    dstId = Column(Integer,
                   ForeignKey('GraphDbVertex.id', ondelete='CASCADE'),
                   nullable=False)
    dst = relationship(GraphDbVertex,
                       primaryjoin="GraphDbEdge.dstId==GraphDbVertex.id")

    __table_args__ = (
        Index("idx_GraphDbEdge_importHash", segmentHash, unique=False),
        Index("idx_GraphDbEdge_modelSet_key", modelSetId, key, unique=True),
    )
