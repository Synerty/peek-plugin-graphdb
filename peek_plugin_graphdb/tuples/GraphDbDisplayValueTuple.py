from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix

from peek_plugin_graphdb._private.storage.GraphDbItem import GraphDbItem
from vortex.Tuple import Tuple, addTupleType

@addTupleType
class GraphDbDisplayValueTuple(Tuple):
    """ Live DB Display Value Tuple

    This tuple stores a value of a key in the Live DB database.

    """
    __tupleType__ = graphdbTuplePrefix + 'GraphDbDisplayValueTuple'
    __slots__ = ("key", "dataType", "rawValue", "displayValue")

    DATA_TYPE_NUMBER_VALUE = GraphDbItem.NUMBER_VALUE
    DATA_TYPE_STRING_VALUE = GraphDbItem.STRING_VALUE
    DATA_TYPE_COLOR = GraphDbItem.COLOR
    DATA_TYPE_LINE_WIDTH = GraphDbItem.LINE_WIDTH
    DATA_TYPE_LINE_STYLE = GraphDbItem.LINE_STYLE
    DATA_TYPE_GROUP_PTR = GraphDbItem.GROUP_PTR