from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix

from vortex.Tuple import Tuple, addTupleType


@addTupleType
class GraphDbRawValueUpdateTuple(Tuple):
    """ Live DB Raw Value Update

    This tuple represents an update to the raw value for a live db item

    """
    __tupleType__ = graphdbTuplePrefix + 'GraphDbRawValueUpdateTuple'
    __slots__ = ("key", "rawValue")
