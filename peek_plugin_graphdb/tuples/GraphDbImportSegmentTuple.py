import hashlib
import json
from typing import List

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbSegmentLinkTuple import GraphDbSegmentLinkTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple


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

    #:  The hash of this import group
    importGroupHash: str = TupleField()

    #:  The edges
    edges: List[GraphDbEdgeTuple] = TupleField([])

    #:  The edges
    vertexes: List[GraphDbVertexTuple] = TupleField([])

    #:  The edges
    links: List[GraphDbSegmentLinkTuple] = TupleField([])

    def generateSegmentKey(self) -> None:
        self.edges.sort(key=lambda e: e.key)
        self.vertexes.sort(key=lambda v: v.key)

        m = hashlib.sha256()
        m.update(b'zeroth item padding')

        for edge in self.edges:
            m.update(str(edge).encode())

        for vertex in self.vertexes:
            m.update(str(vertex).encode())

        self.key = m.hexdigest()

    def generateSegmentHash(self) -> str:
        self.edges.sort(key=lambda e: e.key)
        self.vertexes.sort(key=lambda v: v.key)
        self.links.sort(key=lambda l: l.vertexKey)

        m = hashlib.sha256()
        m.update(b'zeroth item padding')
        m.update(str(self).encode())
        return m.hexdigest()

    def packJson(self, modelSetId: int) -> str:
        packedJsonDict = self.toJsonDict()
        del packedJsonDict['importGroupHash']
        del packedJsonDict['modelSetKey']
        packedJsonDict['_msid'] = modelSetId
        return json.dumps(packedJsonDict, sort_keys=True, indent='')
