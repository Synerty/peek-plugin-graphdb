from peek_plugin_graphdb._private.tuples.ItemKeyTypeTuple import ItemKeyTypeTuple
from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet


@addTupleType
class ItemKeyType(Tuple, DeclarativeBase):
    __tablename__ = 'ItemKeyType'
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyTypeTable'

    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this itemKeyIndex
    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet, lazy=False)

    key = Column(String, nullable=False)
    name = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_DocType_model_key", modelSetId, key, unique=True),
        Index("idx_DocType_model_name", modelSetId, name, unique=True),
    )

    def toTuple(self) -> ItemKeyTypeTuple:
        newTuple = ItemKeyTypeTuple()
        newTuple.id__ = self.id
        newTuple.key = self.key
        newTuple.modelSetKey = self.modelSet.key
        newTuple.name = self.name
        return newTuple
