from typing import List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple


class GraphDbWriteApiABC(metaclass=ABCMeta):
    @abstractmethod
    def importGraphSegment(self, modelSetKey: str, segmentHash: str,
                           vertices: List[GraphDbImportVertexTuple],
                           edges: List[GraphDbImportEdgeTuple]) -> Deferred:
        """ Import Graph Segment

        Import a new segment of the Graph, replacing existing vertices and edges with the
        same segmentHash.

        :param modelSetKey:  The name of the model set for the live db.
        :param segmentHash: The unique segment hash for the graph segment being imported.
        :param vertices: A list of vertices to import / update.
        :param edges: A list of edges to import / update.

        :return: A deferred that fires when the update is complete.
        :rtype: None

        """
