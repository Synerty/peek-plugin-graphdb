from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbEdgeTuple(Tuple):
    """ Graph DB Edge Tuple

    This tuple represents a connection between two vertices.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbEdgeTuple'
    __slots__ = ("id", "key", "srcId", "dstId", "segmentHash", "src", "dst", "props")
