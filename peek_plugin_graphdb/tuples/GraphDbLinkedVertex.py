from typing import Dict, List


class GraphDbLinkedVertex:
    """ Graph DB Linked Vertex

    This tuple is a vertex in the GraphDb plugin.

    """
    __slots__ = ("k", "p", "e", "sk")

    @property
    def key(self) -> str:
        """ Key

        The unique ID of this vertex
        """
        return self.k

    @property
    def props(self) -> Dict[str, str]:
        """ Properties
        """
        if self.p is None:
            self.p = {}
        return self.p

    @property
    def edges(self) -> List:
        """ Edges
            @:rtype List[GraphDbLinkedEdge]
        """
        if self.e is None:
            self.e = []
        return self.e


    @property
    def linksToSegmentKeys(self) -> List[str]:
        """ Next Segment Keys

        The keys of the other segments that this vertex links to.
        """
        if self.e is None:
            self.e = []
        return self.e
