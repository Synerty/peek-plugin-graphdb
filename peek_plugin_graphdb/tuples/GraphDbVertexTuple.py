from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix


@addTupleType
class GraphDbVertexTuple(Tuple):
    """ Graph DB Vertex Tuple

    This tuple represents a vertex in the GraphDB plugin.

    """
    __tupleType__ = graphdbTuplePrefix + 'GraphDbVertexTuple'
    __slots__ = ("id", "key", "name", "desc", "props", "edges")
