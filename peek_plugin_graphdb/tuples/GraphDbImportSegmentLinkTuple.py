from typing import Dict, Any

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class GraphDbImportSegmentLinkTuple(Tuple):
    """ Segment Link Tuple

    This tuple is the publicly exposed Segment Links

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportSegmentLinkTuple'
    __slots__ = ("vk", "sk")

    #:  The key of the vertex that joins the two segments
    vertexKey: str = TupleField()

    #:  The segment that this segment links to
    segmentKey: str = TupleField()

    @property
    def vertexKey(self) -> str:
        return self.vk

    @vertexKey.setter
    def vertexKey(self, val) -> None:
        self.vk = val

    @property
    def segmentKey(self) -> str:
        return self.sk

    @segmentKey.setter
    def segmentKey(self, val) -> None:
        self.sk = val

    def packJsonDict(self) -> Dict[str, Any]:
        return dict(
            vk=self.vk,
            sk=self.sk
        )
