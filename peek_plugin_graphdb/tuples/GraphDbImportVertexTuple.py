from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbImportVertexTuple(Tuple):
    """ Graph DB Import Vertex Tuple

    This tuple represents a vertex that is being imported into the GraphDb plugin.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbDisplayValueTuple'
    __slots__ = ("key", "name", "desc", "propsJson")
