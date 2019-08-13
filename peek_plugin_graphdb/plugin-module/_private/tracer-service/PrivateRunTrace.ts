/** Run Trace

 This module contains the logic to perform typescript side traces.

 NOTE: THIS FILE MUST BE KEPT IN SYNC WITH THE PYTHON VERSION AT :
 * peek_plugin_graphdb/_private/client/controller/RunTrace.py


 */

import {
    PrivateSegmentLoaderService,
    SegmentResultI
} from "../segment-loader/PrivateSegmentLoaderService";
import {GraphDbLinkedVertex} from "../../GraphDbLinkedVertex";
import {GraphDbLinkedEdge} from "../../GraphDbLinkedEdge";
import {GraphDbTraceConfigTuple} from "../tuples/GraphDbTraceConfigTuple";
import {GraphDbTraceResultTuple} from "../../GraphDbTraceResultTuple";
import {GraphDbLinkedSegment} from "../../GraphDbLinkedSegment";
import {GraphDbTraceResultVertexTuple} from "../../GraphDbTraceResultVertexTuple";
import {GraphDbTraceResultEdgeTuple} from "../../GraphDbTraceResultEdgeTuple";
import {GraphDbTraceConfigRuleTuple} from "../tuples/GraphDbTraceConfigRuleTuple";
import * as moment from "moment";

// ----------------------------------------------------------------------------


export class _TraceAbortedWithMessageError extends Error {

}

export interface _TraceEdgeParams {
    segment: GraphDbLinkedSegment;
    edge: GraphDbLinkedEdge;
    vertex: GraphDbLinkedVertex;
}

export class PrivateRunTrace {

    private _alreadyTracedSet = {};
    private _asyncLoadInProgressCount = 0;

    private _traceEdgeQueue: _TraceEdgeParams[] = [];

    private _completeResolve: any = null;
    private _completeReject: any = null;
    private _startTime: Date = null;

    private _traceEnded = false;

    private _traceConfigKey: string;
    private _traceRules: GraphDbTraceConfigRuleTuple[] = [];

    constructor(private _result: GraphDbTraceResultTuple,
                traceConfig: GraphDbTraceConfigTuple,
                private segmentLoader: PrivateSegmentLoaderService,
                private _startVertexOrEdgeKey: string,
                private _startSegmentKeys: string[],
                private _maxVertexes: null | number = null) {

        this._traceConfigKey = traceConfig.key;
        this._traceRules = traceConfig.rules.filter(r => r.isEnabled);
        this._traceRules.sort(this._ruleSortCmp);

    }

    run(): Promise<void> {
        this._startTime = new Date();
        return new Promise<void>((resolve, reject) => {
            this._completeResolve = resolve;
            this._completeReject = reject;

            // Queue up the starting point and any segments it's in
            for (const segmentKey of this._startSegmentKeys) {
                this._getSegment(segmentKey)
                    .then((segment: GraphDbLinkedSegment) => {
                        try {
                            const vertex = segment.vertexByKey[this._startVertexOrEdgeKey];
                            if (vertex) {
                                this._traceVertex(segment, vertex);
                                return;
                            }

                            const edge = segment.edgeByKey[this._startVertexOrEdgeKey];
                            if (edge) {
                                this._traceEdgeQueue.push({
                                    segment: segment,
                                    edge: edge,
                                    vertex: null
                                });
                                return;
                            }

                        } catch (e) {
                            if (e instanceof _TraceAbortedWithMessageError) {
                                this.handleTraceComplete();
                                return
                            }
                            console.log(e);
                            throw e;
                        }

                        throw new Error("Could not find vertex or edge"
                            + ` ${this._startVertexOrEdgeKey} of segment ${segmentKey} `
                        );
                    })
                    .then(() => this.iterate())
                    .catch((e) => this.handlePromiseCatch(e));

            } // End FOR

        });

    }

    // ---------------
    // Helper methods
    // To deal with the need for async promises during the trace
    // These are TYPESCRIPT only methods.

    private _getSegment(segmentKey: string): Promise<GraphDbLinkedSegment> {
        this._asyncLoadInProgressCount++;
        return this.segmentLoader
            .getSegments(this._result.modelSetKey, [segmentKey])
            .then((segmentsByKey: SegmentResultI) => {
                this._asyncLoadInProgressCount--;
                const segment = segmentsByKey[segmentKey];
                if (segment == null) {
                    throw new Error(`Could not find segment ${segmentKey} `);
                }
                return segment;
            });
    }

    private handleTraceComplete() {
        if (this._traceEnded)
            return;

        this._traceEnded = true;

        if (this._result.vertexes.length && !this._result.edges.length) {
            this._result.traceAbortedMessage = "The trace stopped on the start device.";
        }

        const duration = moment
            .duration(new Date().getTime() - this._startTime.getTime())
            .humanize();

        // Log the complete
        console.log(`Trace completed. Trace Config '${this._traceConfigKey}',`
            + ` Start Vertex or Edge '${this._startVertexOrEdgeKey}',`
            + ` ${this._result.vertexes.length} vertexes,`
            + ` ${this._result.edges.length} edges,`
            + ` error:'${this._result.traceAbortedMessage}',`
            + ` in ${duration}`);

        this._completeResolve(this._result);
    }

    private handlePromiseCatch(error: string): void {
        if (this._traceEnded)
            return;

        this._traceEnded = true;

        console.log(`ERROR: ${error}`);
        this._completeReject(`ERROR: ${error}`);
    }


    private iterate(): void {
        // Drain the trace queue
        try {
            while (this._traceEdgeQueue.length && !this._traceEnded) {
                const params = this._traceEdgeQueue.pop();
                this._traceEdge(params.segment, params.edge, params.vertex)
            }
        } catch (e) {
            if (!(e instanceof _TraceAbortedWithMessageError)) {
                console.log(e);
                this.handlePromiseCatch(e.toString());
            }
            return;
        }


        // If the trace has been aborted
        if (this._result.traceAbortedMessage != null) {
            this.handleTraceComplete();

            // OR if the trace has completed
        } else if (this._traceEdgeQueue.length === 0
            && this._asyncLoadInProgressCount === 0) {
            this.handleTraceComplete();
        }

    }

    // ---------------
    // Rule sort comparator

    private _ruleSortCmp(r1: GraphDbTraceConfigRuleTuple,
                         r2: GraphDbTraceConfigRuleTuple): number {
        const R = new GraphDbTraceConfigRuleTuple();

        // First, Order the rules that apply to the start vertex first
        if (r1.applyTo == R.APPLY_TO_START_VERTEX
            && r2.applyTo != R.APPLY_TO_START_VERTEX) {
            return -1;
        }

        if (r1.applyTo != R.APPLY_TO_START_VERTEX
            && r2.applyTo == R.APPLY_TO_START_VERTEX) {
            return 1;
        }

        // Then just compare by order
        return r1.order == r2.order ? 0 : (r1.order < r2.order ? -1 : 1);
    }

    // ---------------
    // Traversing methods

    private _traceEdge(segment: GraphDbLinkedSegment,
                       edge: GraphDbLinkedEdge,
                       fromVertex: GraphDbLinkedVertex | null): void {
        if (this._checkAlreadyTraced({edgeKey: edge.key}))
            return;

        const fromSrcVertex = fromVertex && edge.srcVertex.key == fromVertex.key;
        if (!this._matchTraceRules({edge: edge, fromSrcVertex: fromSrcVertex}))
            return;

        this._addEdge(edge);

        if (fromVertex != null) {
            const toVertex = edge.getOtherVertex(fromVertex.key);
            this._traceVertex(segment, toVertex);

        } else {
            this._traceVertex(segment, edge.srcVertex);
            this._traceVertex(segment, edge.dstVertex);

        }
    }

    private _traceVertex(segment: GraphDbLinkedSegment,
                         vertex: GraphDbLinkedVertex): void {
        if (this._checkAlreadyTraced({vertexKey: vertex.key}))
            return;

        this._addVertex(vertex);

        if (!this._matchTraceRules({vertex: vertex}))
            return;

        for (const edge of vertex.edges) {
            this._traceEdge(segment, edge, vertex);
        }

        for (const segmentKey of vertex.linksToSegmentKeys) {
            this._traceEdgesInNextSegment(vertex.key, segmentKey);
        }

    }

    private _traceEdgesInNextSegment(vertexKey: string, segmentKey: string) {
        this._getSegment(segmentKey)
            .then((segment: GraphDbLinkedSegment) => {
                const vertex = segment.vertexByKey[vertexKey];
                if (vertex == null)
                    throw new Error(`Vertex '${vertexKey}' is not in segment '${segmentKey}'`);

                for (const edge of vertex.edges) {
                    this._traceEdgeQueue.push({
                        segment: segment,
                        edge: edge,
                        vertex: vertex
                    });
                }
            })
            .then(() => this.iterate())
            .catch((e) => this.handlePromiseCatch(e));
    }

    // ---------------
    // Add to _result

    private _setTraceAborted(message: string) {
        this._result.traceAbortedMessage = message;
        throw new _TraceAbortedWithMessageError();
    }

    private _addVertex(vertex: GraphDbLinkedVertex) {
        if (this._maxVertexes && this._result.vertexes.length >= this._maxVertexes) {
            this._setTraceAborted(`Trace exceeded maximum vertexes of ${this._maxVertexes}`);
        }

        let newItem = new GraphDbTraceResultVertexTuple();
        newItem.key = vertex.key;
        newItem.props = vertex.props;
        this._result.vertexes.push(newItem);
    }

    private _addEdge(edge: GraphDbLinkedEdge) {
        let newItem = new GraphDbTraceResultEdgeTuple();
        newItem.key = edge.key;
        newItem.srcVertexKey = edge.srcVertex.key;
        newItem.dstVertexKey = edge.dstVertex.key;
        newItem.props = edge.props;
        this._result.vertexes.push(newItem);
    }

    // ---------------
    // Already Traced State

    private _checkAlreadyTraced(params: { vertexKey?: string, edgeKey?: string }): boolean {
        const val = `${params.vertexKey}, ${params.edgeKey}`;
        const traced = this._alreadyTracedSet[val] !== true;
        if (!traced)
            this._alreadyTracedSet[val] = true;

        return traced;
    }


    // ---------------
    // Match Vertex Rules
    private _matchTraceRules(params: {
        vertex?: GraphDbLinkedVertex,
        edge?: GraphDbLinkedEdge,
        fromSrcVertex?: boolean
    }): boolean {

        const isVertex = params.vertex != null;
        const isEdge = params.edge != null;
        const isStartVertex = isVertex && params.vertex.key == this._startVertexOrEdgeKey;

        const props = params.vertex != null ? params.vertex.props : params.edge.props;

        for (let rule of this._traceRules) {
            // Accept the conditions in which we'll run this rule
            if (rule.applyTo == rule.APPLY_TO_VERTEX && isVertex) {
                // pass

            } else if (rule.applyTo == rule.APPLY_TO_VERTEX && isEdge) {
                // pass

            } else if (rule.applyTo == rule.APPLY_TO_VERTEX && isStartVertex) {
                // pass

            } else {
                // Else, this isn't the right rule for this thing, move onto the next
                continue
            }

            // If the rule doesn't match, then continue
            if (!this._matchProps(props, rule, params.fromSrcVertex, params.edge))
                continue;

            // The rule has matched.

            // Apply the action - Continue
            if (rule.action == rule.ACTION_CONTINUE_TRACE) {
                return true;
            }

            // Apply the action - Abort
            if (rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE) {
                this._setTraceAborted(rule.actionData);
                return false;
            }

            // Apply the action - Stop
            if (rule.action == rule.ACTION_STOP_TRACE)
                return false;


        }
    }

    // ---------------
    // Match The Properties
    private _matchProps(props: {}, rule: GraphDbTraceConfigRuleTuple,
                        fromSrcVertex?: boolean, edge?: GraphDbLinkedEdge) {
        let propVal = (props[rule.propertyName] || '').toString();

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_SIMPLE) {
            return propVal == rule.propertyValue;
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_COMMA_LIST) {
            return rule.preparedValueSet[propVal] === true;
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_REGEX) {
            return rule.preparedRegex.exec(propVal);
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_BITMASK_AND) {
            try {
                return !!(parseInt(propVal) & parseInt(rule.propertyValue));

            } catch {
            }
            return false;
        }

        if (rule.propertyValueType == rule.PROP_VAL_TYPE_DIRECTION) {
            const goingUpstream = fromSrcVertex
                ? edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_DOWNSTREAM
                : edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_UPSTREAM;

            const goingDownstream = fromSrcVertex
                ? edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_UPSTREAM
                : edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_DOWNSTREAM;

            const goingBoth = edge.srcDirection == GraphDbLinkedEdge.DIR_SRC_IS_BOTH;

            let bitVal = 0;
            if (goingDownstream) bitVal += rule.PROP_VAL_TRACE_DOWNSTREAM;
            if (goingUpstream) bitVal += rule.PROP_VAL_TRACE_UPSTREAM;
            if (goingBoth) bitVal += rule.PROP_VAL_TRACE_BOTH;

            try {
                return !!(bitVal & parseInt(rule.propertyValue));
            } catch {
            }
            return false;
        }

        throw new Error(`rule.propertyValueType = ${rule.propertyValueType}`);
    }

}