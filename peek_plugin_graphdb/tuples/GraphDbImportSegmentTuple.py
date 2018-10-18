import hashlib
import json
from typing import List

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportSegmentLinkTuple import \
    GraphDbImportSegmentLinkTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class GraphDbImportSegmentTuple(Tuple):
    """ Import Segment Tuple

    This tuple is the publicly exposed Segment

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportSegmentTuple'

    #:  The unique key of this segment
    key: str = TupleField()

    #:  The model set of this segment
    modelSetKey: str = TupleField()

    #:  The edges
    edges: List[GraphDbImportEdgeTuple] = TupleField([])

    #:  The vertexes
    vertexes: List[GraphDbImportVertexTuple] = TupleField([])

    #:  The links to the other segments
    links: List[GraphDbImportSegmentLinkTuple] = TupleField([])

    #:  The hash of this import group
    importGroupHash: str = TupleField()

    def generateSegmentKey(self) -> None:
        self.edges.sort(key=lambda e: e.key)
        self.vertexes.sort(key=lambda v: v.key)

        m = hashlib.md5()
        m.update(b'zeroth item padding')

        for edge in self.edges:
            m.update(str(edge).encode())

        for vertex in self.vertexes:
            m.update(str(vertex).encode())

        self.key = m.hexdigest()

    def generateSegmentHash(self) -> str:
        self.edges.sort(key=lambda e: e.key)
        self.vertexes.sort(key=lambda v: v.key)
        self.links.sort(key=lambda l: l.vertexKey + l.segmentKey)

        m = hashlib.md5()
        m.update(b'zeroth item padding')
        m.update(str(self).encode())
        return m.hexdigest()

    def packJson(self) -> str:
        jsonDict = dict(
            edges=[i.packJsonDict() for i in self.edges],
            links=[i.packJsonDict() for i in self.links],
            vertexes=[i.packJsonDict() for i in self.vertexes]
        )
        return json.dumps(jsonDict, sort_keys=True, indent='')
