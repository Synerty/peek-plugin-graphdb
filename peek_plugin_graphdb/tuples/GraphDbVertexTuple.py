from typing import Dict

from vortex.Tuple import Tuple, addTupleType

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix


@addTupleType
class GraphDbVertexTuple(Tuple):
    """ Graph DB Vertex Tuple

    This tuple represents a vertex in the GraphDb plugin.

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbVertexTuple'
    __slots__ = ("k", "p")
    __rawJonableFields__ = ["p"]

    @property
    def key(self) -> str:
        return self.k

    @key.setter
    def key(self, val) -> None:
        self.k = val

    @property
    def props(self) -> Dict[str, str]:
        if not self.p:
            self.p = {}
        return self.p

    @props.setter
    def props(self, val) -> None:
        self.p = val

    def __repr__(self):
        return '%s.%s' % (self.k, self.p)
