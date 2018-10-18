from typing import Dict

from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex


class GraphDbLinkedEdge:
    """ Graph DB Linked Edge

    This tuple is a connection between two vertices.

    """
    __slots__ = ("k", "s", "d", "p")

    @property
    def key(self) -> str:
        return self.k

    @property
    def srcVertex(self) -> GraphDbLinkedVertex:
        return self.s

    @property
    def dstVertex(self) -> GraphDbLinkedVertex:
        return self.d

    @property
    def props(self) -> Dict[str, str]:
        if self.p is None:
            self.p = {}
        return self.p

    def getOtherVertex(self, vertexKey:str) -> GraphDbLinkedVertex:
        if self.srcVertex.key == vertexKey:
            return self.dstVertex
        return self.srcVertex