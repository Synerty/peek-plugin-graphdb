import json

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


class GraphDbModelSetTuple(object):
    pass


@addTupleType
class ItemKeyTuple(Tuple):
    """ ItemKeyIndex Tuple

    This tuple is the publicly exposed ItemKeyIndex

    """
    __tupleType__ = graphDbTuplePrefix + 'ItemKeyTuple'

    #:  The unique key of this itemKeyIndex
    key: str = TupleField()

    #:  The model set of this itemKeyIndex
    modelSet: GraphDbModelSetTuple = TupleField()

    #:  The itemKeyIndex type
    itemType: int = TupleField()
    ITEM_TYPE_VERTEX = 1
    ITEM_TYPE_EDGE = 2

    #:  The key of the vertex or edge
    itemKey: str = TupleField()

    #:  The key of the segment where it's stored
    segmentKey: str = TupleField()

    @classmethod
    def unpackJson(self, key: str, packedJson: str):
        # Reconstruct the data
        objectProps: {} = json.loads(packedJson)

        # Get out the object type
        thisModelSetId = objectProps['_msid']

        # Create the new object
        newSelf = ItemKeyTuple()

        # These objects get replaced with the full object in the UI
        newSelf.modelSet = GraphDbModelSetTuple(id=thisModelSetId)

        # Unpack the custom data here

        newSelf.itemKey = key
        newSelf.itemType = objectProps.get('itemType')
        newSelf.segmentKeys = objectProps.get('segmentKeys')

        return newSelf
