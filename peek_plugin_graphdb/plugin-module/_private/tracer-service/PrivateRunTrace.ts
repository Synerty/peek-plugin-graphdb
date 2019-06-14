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

// ----------------------------------------------------------------------------


export class _TraceAbortedWithMessageError extends Error {

}


export class RunTrace {

    private _alreadyTracedSet = {};

    _traceConfig: GraphDbTraceConfigTuple;

    constructor(private result: GraphDbTraceResultTuple,
                private segmentLoader: PrivateSegmentLoaderService) {


    }

    run(startVertexKey: string, startSegmentKeys: string[]): Promise<any> {

        try {
            return this._traceSegments(startVertexKey, startSegmentKeys);

        } catch (_TraceAbortedWithMessageError) {
        }

        return Promise.resolve();

    }

    private _traceSegments(vertexKey: string, segmentKeys: string[]): Promise<void> | null {
        let promises = [];
        for (let segmentKey of segmentKeys) {
            let optionalPromise = this._traceSegment(vertexKey, segmentKey);
            if (optionalPromise != null)
                promises.push(optionalPromise);
        }
        return Promise.all(promises)
            .then(() => null);
    }

    private _traceSegment(vertexKey: string, segmentKey: string): Promise<void> | null {
        if (this._checkAlreadyTraced(vertexKey, null, segmentKey))
            return null;

        return this.segmentLoader
            .getSegments(this.result.modelSetKey, [segmentKey])
            .then((segmentsByKey: SegmentResultI) => {
                if (segmentsByKey[segmentKey] == null) {
                    throw new Error(`Could not find segment ${segmentKey}`);
                }

                let segment = segmentsByKey[segmentKey];

                let vertex = segment.vertexByKey[vertexKey];
                if (!vertex) {
                    throw new Error("Could not find vertex"
                        + ` ${vertexKey} of segment ${segmentKey}`
                    );
                }

                return this._traceVertex(vertex, segment);
            });
    }

    private _traceVertex(vertex: GraphDbLinkedVertex,
                         segment: GraphDbLinkedSegment): Promise<void> | null {
        if (this._checkAlreadyTraced(vertex.key, null, segment.key))
            return null;

        this._addToAlreadyTraced(vertex.key, null, segment.key);

        this._addVertex(vertex);

        let rule = this._matchVertexTraceRules(vertex);
        if (rule != null) {
            if (rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE) {
                this._setTraceAborted(rule.actionData);
                return null;
            }

            if (rule.action == rule.ACTION_STOP_TRACE) {
                return null;
            }
        }

        let promises = [];
        for (let edge of vertex.edges) {
            let optionalPromise = this._traceEdge(edge, vertex, segment);
            if (optionalPromise != null)
                promises.push(optionalPromise);
        }

        if (promises.length == 0 && vertex.linksToSegmentKeys.length == 0)
            return null;

        return Promise.all(promises)
            .then(() => {

                if (vertex.linksToSegmentKeys.length == 0)
                    return null;

                return this._traceSegments(vertex.key, vertex.linksToSegmentKeys);
            });
    }

    private _traceEdge(edge: GraphDbLinkedEdge,
                       fromVertex: GraphDbLinkedVertex,
                       segment: GraphDbLinkedSegment): Promise<void> | null {
        let rule = this._matchEdgeTraceRules(edge);
        if (rule != null) {
            if (rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE) {
                this._setTraceAborted(rule.actionData);
                return;
            }

            // Don't trace further along this path.
            if (rule.action == rule.ACTION_STOP_TRACE)
                return;
        }

        this._addEdge(edge);

        let toVertex = edge.getOtherVertex(fromVertex.key);
        return this._traceVertex(toVertex, segment);
    }

    // ---------------
    // Add to result

    private _addVertex(vertex: GraphDbLinkedVertex) {
        let newItem = new GraphDbTraceResultVertexTuple();
        newItem.key = vertex.key;
        newItem.props = vertex.props;
        this.result.vertexes.push(newItem);
    }

    private _addEdge(edge: GraphDbLinkedEdge) {
        let newItem = new GraphDbTraceResultEdgeTuple();
        newItem.key = edge.key;
        newItem.srcVertexKey = edge.srcVertex.key;
        newItem.dstVertexKey = edge.dstVertex.key;
        newItem.props = edge.props;
        this.result.vertexes.push(newItem);
    }

    private _setTraceAborted(message: string) {
        this.result.traceAbortedMessage = message;
        throw new _TraceAbortedWithMessageError();
    }

    // ---------------
    // Already Traced State

    private _checkAlreadyTraced(vertexKey: string | null, edgeKey: string | null,
                                segmentKey: string): boolean {
        let val = `${vertexKey}, ${edgeKey}, ${segmentKey}`;
        return this._alreadyTracedSet[val] === true;
    }

    private _addToAlreadyTraced(vertexKey: string | null, edgeKey: string | null,
                                segmentKey: string) {
        let val = `${vertexKey}, ${edgeKey}, ${segmentKey}`;
        this._alreadyTracedSet[val] = true;
    }

    // ---------------
    // Match Edge Rules
    private _matchEdgeTraceRules(edge: GraphDbLinkedEdge) {
        for (let rule of this._traceConfig.rules) {
            if (rule.applyTo != rule.APPLY_TO_EDGE)
                continue;

            if (this._matchProps(edge.props, rule))
                return rule;
        }
    }


    // ---------------
    // Match Vertex Rules
    private _matchVertexTraceRules(vertex: GraphDbLinkedVertex) {
        for (let rule of this._traceConfig.rules) {
            if (rule.applyTo != rule.APPLY_TO_VERTEX)
                continue;

            if (this._matchProps(vertex.props, rule))
                return rule;
        }
    }

    // ---------------
    // Match The Properties
    private _matchProps(props: {}, rule: GraphDbTraceConfigRuleTuple) {
        if (!rule.isEnabled)
            return false;

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
                return ((parseInt(propVal) & parseInt(rule.propertyValue)) !== 0);

            } catch {
            }
            return false;
        }

        throw new Error("NotImplementedError");
    }
}