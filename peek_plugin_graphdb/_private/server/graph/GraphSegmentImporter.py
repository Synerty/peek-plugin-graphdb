import logging
import ujson as json
from typing import List

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger

from peek_plugin_graphdb._private.server.GraphDBReadApi import GraphDBReadApi
from peek_plugin_graphdb._private.server.controller.MainController import MainController
from peek_plugin_graphdb._private.server.graph.GraphModel import GraphModel
from peek_plugin_graphdb._private.server.graph.GraphUpdateContext import \
    GraphUpdateContext
from peek_plugin_graphdb.tuples.GraphDbEdgeTuple import GraphDbEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple
from peek_plugin_graphdb.tuples.GraphDbVertexTuple import GraphDbVertexTuple

logger = logging.getLogger(__name__)


class GraphSegmentImporter:
    """ GraphDB Import Controller
    """

    def __init__(self, mainController: MainController):
        self._mainController = mainController

    def setReadApi(self, readApi: GraphDBReadApi):
        self._readApi = readApi

    def shutdown(self):
        self._readApi = None

    @inlineCallbacks
    def importGraphSegment(self, modelSetKey: str, segmentHash: str,
                           vertices: List[GraphDbImportVertexTuple],
                           edges: List[GraphDbImportEdgeTuple]) -> Deferred:
        """ Import Graph Segment

        1) set the  coordSetId

        2) Drop all disps with matching importGroupHash

        :param modelSetKey:  The name of the model set for the live db.
        :param segmentHash: The unique segment hash for the graph segment being imported.
        :param vertices: A list of vertices to import / update.
        :param edges: A list of edges to import / update.

        :return: A deferred that fires when the update is complete.
        :rtype: None
        :return:
        """

        graphModel = yield self._mainController.graphForModelSetKey(modelSetKey)
        context = graphModel.newUpdateContext()
        yield self._checkForVerticesToDelete(graphModel, context, segmentHash, edges)
        yield self._importGraphSegment(graphModel, context, segmentHash, vertices, edges)

        yield context.save()

    @deferToThreadWrapWithLogger(logger)
    def _importGraphSegment(self, graphModel: GraphModel,
                            context: GraphUpdateContext,
                            segmentHash: str,
                            vertices: List[GraphDbImportVertexTuple],
                            edges: List[GraphDbImportEdgeTuple]) -> Deferred:

        existingEdgesByKeySrcDst = {}
        for existingEdge in graphModel.edgesForSegmentHash(segmentHash):
            key = (existingEdge.key, existingEdge.src.key, existingEdge.dst.key)
            existingEdgesByKeySrcDst[key] = existingEdge

        vertexByKey = {}

        # Import Vortex -----
        for importVertex in vertices:
            importPropsJson = json.loads(importVertex.propsJson)
            existingVertex = graphModel.vertexForKey(importVertex.key)

            if existingVertex:
                vertexByKey[existingVertex.key] = existingVertex

                # Check attributes
                updatedAttributes = {}
                if importVertex.name != existingVertex.name:
                    updatedAttributes["name"] = newVertex.name

                if importVertex.desc != existingVertex.desc:
                    updatedAttributes["desc"] = newVertex.desc

                if updatedAttributes:
                    context.updateVertexAttributes(existingVertex.key, updatedAttributes)

                # Check properties
                existingPropsJson = json.dumps(existingVertex.json, sort_keys=True)
                if existingPropsJson != importVertex.propsJson:
                    context.updateVertexProps(existingVertex.key, importPropsJson)


            else:
                newVertex = GraphDbVertexTuple(
                    key=importVertex.key,
                    name=importVertex.name,
                    desc=importVertex.desc,
                    props=importPropsJson,
                    edges=tuple()
                )
                vertexByKey[importVertex.key] = newVertex
                context.addVertex(newVertex)

        # Import Edge -----
        for importEdge in edges:

            srcVertex = vertexByKey.get(importEdge.srcKey)
            if not srcVertex:
                raise Exception("Vertex %s was not imported with edge %s",
                                importEdge.srcKey, importEdge.key)

            dstVertex = vertexByKey.get(importEdge.dstKey)
            if not dstVertex:
                raise Exception("Vertex %s was not imported with edge %s",
                                importEdge.dstKey, importEdge.key)

            existingEdge = existingEdgesByKeySrcDst.pop(
                (importEdge.key, importEdge.srcKey, importEdge.dstKey),
                None
            )

            importPropsJson = json.loads(importEdge.propsJson)

            if existingEdge:
                # Check properties
                existingPropsJson = json.dumps(existingVertex.json, sort_keys=True)
                if existingPropsJson != importEdge.propsJson:
                    context.updateVertexProps(existingVertex.key, importPropsJson)

            else:
                newEdge = GraphDbEdgeTuple(
                    key=importEdge.key,
                    name=importEdge.name,
                    desc=importEdge.desc,
                    props=importEdge.props,
                    edges=tuple()
                )
                context.addEdge(newEdge)

        for oldEdge in existingEdgesByKeySrcDst.values():
            context.deleteEdge(oldEdge)

    @deferToThreadWrapWithLogger(logger)
    def _checkForVerticesToDelete(self, graphModel: GraphModel,
                                  context: GraphUpdateContext,
                                  segmentHash: str,
                                  edges: List[GraphDbImportEdgeTuple]):

        newEdgeVertexKeys = set()
        for edge in edges:
            newEdgeVertexKeys.add(edge.srcKey)
            newEdgeVertexKeys.add(edge.dstKey)

        existingVertices = set()
        for edge in graphModel.edgesForSegmentHash(segmentHash):
            existingVertices.add(edge.src)
            existingVertices.add(edge.dst)

        for vertex in existingVertices:
            # If we're importing a new edge that connects to the vertex, then keep it
            if vertex.key in newEdgeVertexKeys:
                continue

            # Otherwise, if only edges from this segment hash connect to it, delete it.
            keep = False
            for edge in vertex.edges:
                if edge.segmentHash != segmentHash:
                    keep = True
                    break

            if not keep:
                context.deleteVertex(vertex.key)
