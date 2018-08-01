from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class GraphDbSegmentTypeTuple(Tuple, DeclarativeBase):
    __tupleType__ = graphDbTuplePrefix + 'GraphDbSegmentTypeTuple'
    __tablename__ = 'GraphDbSegmentType'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this segment
    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet)

    name = Column(String, nullable=False)
    title = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_DocType_model_name", modelSetId, name, unique=True),
        Index("idx_DocType_model_title", modelSetId, title, unique=True),
    )
