from typing import Dict

from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbEdgeTuple(Tuple):
    """ Graph DB Edge Tuple

    This tuple represents a connection between two vertices.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbEdgeTuple'
    __slots__ = ("k", "sk", "dk", "p")
    __rawJonableFields__ = ["p"]

    @property
    def key(self) -> str:
        return self.k

    @key.setter
    def key(self, val) -> None:
        self.k = val

    @property
    def srcVertexKey(self) -> str:
        return self.sk

    @srcVertexKey.setter
    def srcVertexKey(self, val) -> None:
        self.sk = val

    @property
    def dstVertexKey(self) -> str:
        return self.dk

    @dstVertexKey.setter
    def dstVertexKey(self, val) -> None:
        self.dk = val

    @property
    def props(self) -> Dict[str, str]:
        if not self.p:
            self.p = {}
        return self.p

    @props.setter
    def props(self, val) -> None:
        self.p = val
