from peek_plugin_graphdb._private.PluginNames import graphdbTuplePrefix

from vortex.Tuple import Tuple, addTupleType


@addTupleType
class LiveDbRawValueTuple(Tuple):
    """ Live DB Raw Value Tuple

    This tuple represents a raw key / value pair in the Live Db

    """
    __tupleType__ = graphdbTuplePrefix + 'LiveDbRawValueTuple'
    __slots__ = ("id", "key", "rawValue")

    def __init__(self, id=None, key=None, rawValue=None):
        # DON'T CALL SUPER INIT
        self.id = id
        self.key = key
        self.rawValue = rawValue
