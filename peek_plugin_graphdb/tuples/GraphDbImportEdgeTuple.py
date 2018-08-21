from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbImportEdgeTuple(Tuple):
    """ Graph DB Import Edge Tuple

    This tuple represents a connection between two vertices that is being imported into
    the GraphDb plugin.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportEdgeTuple'
    __slots__ = ("key", "srcKey", "dstKey", "propsJson")
