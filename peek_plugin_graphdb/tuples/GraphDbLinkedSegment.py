from collections import defaultdict
from typing import Dict

from peek_plugin_graphdb.tuples.GraphDbLinkedEdge import GraphDbLinkedEdge
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex


class GraphDbLinkedSegment:
    """ Linked Segment

    This tuple is the publicly exposed Segment

    """
    #:  The unique key of this segment
    key: str = None

    #:  The model set of this segment
    modelSetKey: str = None

    #:  The edges
    edgeByKey: Dict[str, GraphDbLinkedEdge] = {}

    #:  The vertexes
    vertexByKey: Dict[str, GraphDbLinkedVertex] = {}

    def unpackJson(self, jsonDict: Dict, segmentKey: str,
                   modelSetKey: str) -> 'GraphDbLinkedSegment':
        self.key = segmentKey
        self.modelSetKey = modelSetKey

        linksToSegmentKeysByVertexKey = defaultdict(list)
        for jsonLink in jsonDict["links"]:
            linksToSegmentKeysByVertexKey[jsonLink["vk"]].append(jsonLink["sk"])

        for jsonVertex in jsonDict["vertexes"]:
            newVertex = GraphDbLinkedVertex()
            newVertex.k = jsonVertex["k"]
            newVertex.p = jsonVertex["p"]
            if newVertex.key in linksToSegmentKeysByVertexKey:
                newVertex.sk = linksToSegmentKeysByVertexKey[newVertex.key]
            self.vertexByKey[newVertex.key] = newVertex

        for jsonEdge in jsonDict["edges"]:
            newEdge = GraphDbLinkedEdge()
            newEdge.k = jsonEdge["k"]
            newEdge.p = jsonEdge["p"]
            newEdge.s = self.vertexByKey[jsonEdge["sk"]]
            newEdge.d = self.vertexByKey[jsonEdge["dk"]]
            newEdge.srcVertex.e.append(newEdge)
            newEdge.dstVertex.e.append(newEdge)
            self.edgeByKey[newEdge.key] = newEdge

        return self
