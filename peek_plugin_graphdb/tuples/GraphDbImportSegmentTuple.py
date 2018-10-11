import hashlib
import json

from vortex.Tuple import addTupleType, TupleField

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbSegmentTuple import GraphDbSegmentTuple


@addTupleType
class GraphDbImportSegmentTuple(GraphDbSegmentTuple):
    """ Import Segment Tuple

    This tuple is the publicly exposed Segment

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportSegmentTuple'

    #:  The hash of this import group
    importGroupHash: str = TupleField()

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
