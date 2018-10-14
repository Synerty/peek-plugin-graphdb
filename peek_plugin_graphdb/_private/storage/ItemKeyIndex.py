from sqlalchemy import Column, Index, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.storage.DeclarativeBase import DeclarativeBase
from peek_plugin_graphdb._private.storage.ItemKeyType import \
    ItemKeyType
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class ItemKeyIndex(Tuple, DeclarativeBase):
    __tablename__ = 'ItemKeyIndex'
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyIndexTable'

    #:  The unique ID of this itemKeyIndex (database generated)
    id = Column(Integer, primary_key=True, autoincrement=True)

    #:  The model set for this itemKeyIndex
    modelSetId = Column(Integer,
                        ForeignKey('GraphDbModelSet.id', ondelete='CASCADE'),
                        nullable=False)
    modelSet = relationship(GraphDbModelSet)

    #:  The model set for this itemKeyIndex
    itemKeyTypeId = Column(Integer,
                            ForeignKey('ItemKeyType.id', ondelete='CASCADE'),
                            nullable=False)
    itemKeyType = relationship(ItemKeyType)

    importGroupHash = Column(String, nullable=False)

    #:  The unique key of this itemKeyIndex
    key = Column(String, nullable=False)

    #:  The chunk that this itemKeyIndex fits into
    chunkKey = Column(String, nullable=False)

    #:  The JSON ready for the Compiler to use
    packedJson = Column(String, nullable=False)

    __table_args__ = (
        Index("idx_ItemKeyIndex_key", modelSetId, key, unique=True),
        Index("idx_ItemKeyIndex_item_keyType", itemKeyTypeId, unique=False),
        Index("idx_ItemKeyIndex_gridKey", chunkKey, unique=False),
        Index("idx_ItemKeyIndex_importGroupHash", importGroupHash, unique=False),
    )
