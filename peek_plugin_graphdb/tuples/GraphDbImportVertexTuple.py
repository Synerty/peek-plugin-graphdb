from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix


@addTupleType
class GraphDbImportVertexTuple(Tuple):
    """ Graph DB Import Vertex Tuple

    This tuple represents a vertex that is being imported into the GraphDB plugin.

    """
    __tupleType__ = graphdbTuplePrefix + 'GraphDbDisplayValueTuple'
    __slots__ = ("key", "name", "desc", "propsJson")
