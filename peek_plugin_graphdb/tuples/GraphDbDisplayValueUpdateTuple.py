from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix

from vortex.Tuple import Tuple, addTupleType


@addTupleType
class GraphDbDisplayValueUpdateTuple(Tuple):
    """ Live DB Display Value Update

    This tuple represents an update to the display value for a live db item

    """
    __tupleType__ = graphdbTuplePrefix + 'GraphDbDisplayValueUpdateTuple'
    __slots__ = ("key", "displayValue")
