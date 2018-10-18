""" Fast Graph DB

This module stores a memory resident model of a graph network.

"""
import logging
import re
from typing import List, Dict, Optional

from peek_plugin_graphdb._private.client.controller.FastGraphDb import FastGraphDb, \
    FastGraphDbModel
from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    TraceConfigCacheController
from peek_plugin_graphdb.tuples.GraphDbLinkedEdge import GraphDbLinkedEdge
from peek_plugin_graphdb.tuples.GraphDbLinkedSegment import GraphDbLinkedSegment
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex
from peek_plugin_graphdb.tuples.GraphDbTraceConfigRuleTuple import \
    GraphDbTraceConfigRuleTuple
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple
from peek_plugin_graphdb.tuples.GraphDbTraceResultTuple import GraphDbTraceResultTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class _TraceAbortedWithMessageException(Exception):
    pass


class TracerController:
    def __init__(self, fastGraphDb: FastGraphDb,
                 itemKeyCacheController: ItemKeyIndexCacheController,
                 traceConfigCacheController: TraceConfigCacheController):
        self._fastGraphDb = fastGraphDb
        self._itemKeyCacheController = itemKeyCacheController
        self._traceConfigCacheController = traceConfigCacheController

    def shutdown(self):
        self._fastGraphDb = None
        self._itemKeyCacheController = None
        self._traceConfigCacheController = None

    @deferToThreadWrapWithLogger(logger)
    def runTrace(self, modelSetKey, traceConfigKey,
                 startVertexKey) -> GraphDbTraceResultTuple:
        traceConfig = self._traceConfigCacheController.traceConfigTuple(
            modelSetKey=modelSetKey, traceConfigKey=traceConfigKey
        )

        # Prepossess some trace rules
        traceConfig = traceConfig.tupleClone()
        for rule in traceConfig.rules:
            if rule.propertyValueType == rule.PROP_VAL_TYPE_COMMA_LIST:
                rule.propertyValue = set(rule.propertyValue.split(','))

            elif rule.propertyValueType == rule.PROP_VAL_TYPE_REGEX:
                rule.propertyValue = re.compile(rule.propertyValue)

        startSegmentKeys = self._itemKeyCacheController.getSegmentKeys(
            modelSetKey=modelSetKey, vertexKey=startVertexKey
        )

        fastGraphDbModel = self._fastGraphDb.graphForModelSet(modelSetKey)

        return _RunTrace(traceConfig, fastGraphDbModel,
                         startVertexKey, startSegmentKeys).run()


class _RunTrace:
    def __init__(self, traceConfig: GraphDbTraceConfigTuple,
                 fastDb: FastGraphDbModel,
                 startVertexKey: str, startSegmentKeys: List[str]) -> None:

        self._traceConfig = traceConfig
        self._fastDb = fastDb
        self._startVertexKey = startVertexKey
        self._startSegmentKeys = startSegmentKeys

        self._alreadyTracedSet = set()
        self._result = GraphDbTraceResultTuple()

    def run(self) -> GraphDbTraceResultTuple:

        try:
            for segmentKey in self._startSegmentKeys:
                self._traceSegment(self._startVertexKey, segmentKey)

        except _TraceAbortedWithMessageException:
            pass

        return self._result

    def _traceSegment(self, vertexKey: str, segmentKey: str) -> None:
        if self._checkAlreadyTraced(vertexKey, None, segmentKey):
            return

        self._addToAlreadyTraced(vertexKey, None, segmentKey)

        segment = self._fastDb.getSegment(segmentKey)
        if not segment:
            raise Exception("Could not find segment %s", segmentKey)

        vertex = segment.vertexByKey.get(vertexKey)
        if not vertex:
            raise Exception("Could not find vertex %s in segment %s",
                            vertexKey, segment.key)

        self._traceVertex(vertex, segment)

    def _traceVertex(self, vertex: GraphDbLinkedVertex,
                     segment: GraphDbLinkedSegment) -> None:
        if self._checkAlreadyTraced(vertex.key, None, segment.key):
            return

        self._addToAlreadyTraced(vertex.key, None, segment.key)

        self._addVertex(vertex)

        rule = self._matchVertexTraceRules(vertex)
        if rule:
            if rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE:
                self._setTraceAborted(rule.actionData)
                return

            if rule.action == rule.ACTION_STOP_TRACE:
                return

        for edge in vertex.edges:
            self._traceEdge(edge, vertex, segment)

        if vertex.linksToSegmentKeys:
            for segmentKey in vertex.linksToSegmentKeys:
                self._traceSegment(vertex.key, segmentKey)

    def _traceEdge(self, edge: GraphDbLinkedEdge,
                   fromVertex: GraphDbLinkedVertex,
                   segment: GraphDbLinkedSegment):
        rule = self._matchEdgeTraceRules(edge)
        if rule:
            if rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE:
                self._setTraceAborted(rule.actionData)
                return

            # Don't trace further along this path.
            if rule.action == rule.ACTION_STOP_TRACE:
                return

        toVertex = edge.getOtherVertex(fromVertex.key)
        self._traceVertex(toVertex, segment)

    # ---------------
    # Add to result

    def _addVertex(self, vertex: GraphDbLinkedVertex):
        # TODO Handle the case when the vertex is added that belongs in both segments
        pass

    def _addEdge(self, edge: GraphDbLinkedEdge):
        pass

    def _setTraceAborted(self, message: str):
        pass

    # ---------------
    # Already Traced State

    def _checkAlreadyTraced(self, vertexKey: Optional[str], edgeKey: Optional[str],
                            segmentKey: str) -> bool:
        return (vertexKey, edgeKey, segmentKey) in self._alreadyTracedSet

    def _addToAlreadyTraced(self, vertexKey: Optional[str], edgeKey: Optional[str],
                            segmentKey: str):
        self._alreadyTracedSet.add((vertexKey, edgeKey, segmentKey))

    # ---------------
    # Match Edge Rules
    def _matchEdgeTraceRules(self, edge: GraphDbLinkedEdge):
        for rule in self._traceConfig.rules:
            if rule.applyTo != rule.APPLY_TO_EDGE:
                continue

            if self._matchProps(edge.props, rule):
                return rule

    # ---------------
    # Match Vertex Rules
    def _matchVertexTraceRules(self, vertex: GraphDbLinkedVertex):
        for rule in self._traceConfig.rules:
            if rule.applyTo != rule.APPLY_TO_VERTEX:
                continue

            if self._matchProps(vertex.props, rule):
                return rule

    # ---------------
    # Match The Properties
    def _matchProps(self, props: Dict,
                    rule: GraphDbTraceConfigRuleTuple):
        propVal = str(props.get(rule.propertyName))

        if rule.propertyValueType == rule.PROP_VAL_TYPE_SIMPLE:
            if propVal == rule.propertyValue:
                return True

        if rule.propertyValueType == rule.PROP_VAL_TYPE_COMMA_LIST:
            return propVal in rule.propertyValue

        if rule.propertyValueType == rule.PROP_VAL_TYPE_REGEX:
            return rule.propertyValue.match(propVal)

        if rule.propertyValueType == rule.PROP_VAL_TYPE_BITMASK_AND:
            try:
                if int(propVal) & int(rule.propertyValue):
                    return True
            except:
                return False

        raise NotImplementedError()
