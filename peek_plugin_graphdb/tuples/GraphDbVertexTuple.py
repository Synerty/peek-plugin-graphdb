from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbVertexTuple(Tuple):
    """ Graph DB Vertex Tuple

    This tuple represents a vertex in the GraphDb plugin.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbVertexTuple'
    __slots__ = ("id", "key", "name", "desc", "props", "edges")
