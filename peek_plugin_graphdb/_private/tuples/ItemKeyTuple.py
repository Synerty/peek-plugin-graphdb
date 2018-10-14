import json
from typing import Dict

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb._private.tuples.ItemKeyTypeTuple import ItemKeyTypeTuple
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
    itemKeyType: ItemKeyTypeTuple = TupleField()

    #:  A string value of the itemKey
    valueStr: Dict = TupleField()

    #:  An int value of the itemKey
    valueInt: Dict = TupleField()

    # Add more values here

    @classmethod
    def unpackJson(self, key: str, packedJson: str):
        # Reconstruct the data
        objectProps: {} = json.loads(packedJson)

        # Get out the object type
        thisItemKeyTypeId = objectProps['_tid']

        # Get out the object type
        thisModelSetId = objectProps['_msid']

        # Create the new object
        newSelf = ItemKeyTuple()

        newSelf.key = key

        # These objects get replaced with the full object in the UI
        newSelf.modelSet = GraphDbModelSetTuple(id__=thisModelSetId)
        newSelf.itemKeyType = ItemKeyTypeTuple(id__=thisItemKeyTypeId)

        # Unpack the custom data here
        newSelf.valueStr = objectProps.get('valueStr')
        newSelf.valueInt = objectProps.get('valueInt')

        return newSelf
