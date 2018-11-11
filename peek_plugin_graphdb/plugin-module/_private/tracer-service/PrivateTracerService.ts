import {Injectable} from "@angular/core";

import {
    ComponentLifecycleEventEmitter,
    extend,
    Payload,
    PayloadEnvelope,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService
} from "@synerty/vortexjs";


import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";

import {OfflineConfigTuple} from "../tuples/OfflineConfigTuple";
import {
    PrivateSegmentLoaderService,
    SegmentResultI
} from "../segment-loader/PrivateSegmentLoaderService";
import {GraphDbTupleService} from "../GraphDbTupleService";
import {GraphDbLinkedVertex} from "../../GraphDbLinkedVertex";
import {GraphDbLinkedEdge} from "../../GraphDbLinkedEdge";
import {GraphDbTraceConfigTuple} from "../tuples/GraphDbTraceConfigTuple";
import {ItemKeyIndexLoaderService} from "../item-key-index-loader";
import {GraphDbTraceResultTuple} from "../../GraphDbTraceResultTuple";
import {GraphDbLinkedSegment} from "../../GraphDbLinkedSegment";
import {GraphDbTraceResultVertexTuple} from "../../GraphDbTraceResultVertexTuple";
import {GraphDbTraceResultEdgeTuple} from "../../GraphDbTraceResultEdgeTuple";
import {GraphDbTraceConfigRuleTuple} from "../tuples/GraphDbTraceConfigRuleTuple";

// ----------------------------------------------------------------------------


class _TraceAbortedWithMessageError extends Error {

}

// ----------------------------------------------------------------------------
/** Tracer
 *
 * This class either asks the server for the trace result or traces locally
 *
 */
@Injectable()
export class PrivateTracerService extends ComponentLifecycleEventEmitter {

    private offlineConfig: OfflineConfigTuple = new OfflineConfigTuple();


    constructor(private vortexService: VortexService,
                private vortexStatusService: VortexStatusService,
                private segmentLoader: PrivateSegmentLoaderService,
                private itemKeyLoader: ItemKeyIndexLoaderService,
                private tupleService: GraphDbTupleService) {
        super();

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(new TupleSelector(OfflineConfigTuple.tupleName, {}),
                false, false, true)
            .takeUntil(this.onDestroyEvent)
            .filter(v => v.length != 0)
            .subscribe((tuples: OfflineConfigTuple[]) => {
                this.offlineConfig = tuples[0];
            });


    }

    private loadTraceConfig(modelSetKey: string,
                            traceConfigKey: string): Promise<GraphDbTraceConfigTuple | null> {
        let ts = new TupleSelector(GraphDbTraceConfigTuple.tupleName, {});
        let promise = this.tupleService.offlineObserver
            .promiseFromTupleSelector(ts)
            .then((tuples: GraphDbTraceConfigTuple[]) => {
                if (!tuples.length)
                    return null;

                for (let tuple of tuples) {
                    if (tuple.modelSet.key == modelSetKey
                        && tuple.key == traceConfigKey) {
                        return tuple;
                    }
                }
                return null;
            });
        return promise;
    }

    /** Get Segments
     *
     * Get the objects with matching keywords from the index..
     *
     */
    runTrace(modelSetKey: string, traceConfigKey: string,
             startVertexKey: string): Promise<GraphDbTraceResultTuple> {

        if (modelSetKey == null || modelSetKey.length == 0) {
            return Promise.reject("We've been passed a null/empty modelSetKey");
        }

        if (traceConfigKey == null || traceConfigKey.length == 0) {
            return Promise.reject("We've been passed a null/empty traceConfigKey");
        }

        if (startVertexKey == null || startVertexKey.length == 0) {
            return Promise.reject("We've been passed a null/empty startVertexKey");
        }

        if (!this.offlineConfig.cacheChunksForOffline
            || this.vortexStatusService.snapshot.isOnline) {
            return this.runServerTrace(modelSetKey, traceConfigKey, startVertexKey);
        }

        return this.runLocalTrace(modelSetKey, traceConfigKey, startVertexKey);
    }

    private runServerTrace(modelSetKey: string, traceConfigKey: string,
                           startVertexKey: string): Promise<GraphDbTraceResultTuple> {

        let ts = new TupleSelector(GraphDbTraceResultTuple.tupleName, {
            "modelSetKey": modelSetKey,
            "traceConfigKey": traceConfigKey,
            "startVertexKey": startVertexKey
        });

        let isOnlinePromise: any = this.vortexStatusService.snapshot.isOnline ?
            Promise.resolve() :
            this.vortexStatusService.isOnline
                .filter(online => online)
                .first()
                .toPromise();

        return isOnlinePromise
            .then(() => this.tupleService.offlineObserver.pollForTuples(ts, false));
    }

    private runLocalTrace(modelSetKey: string, traceConfigKey: string,
                          startVertexKey: string): Promise<GraphDbTraceResultTuple> {

        let result = new GraphDbTraceResultTuple();
        result.modelSetKey = modelSetKey;
        result.traceConfigKey = traceConfigKey;
        result.startVertexKey = startVertexKey;


        let runTrace = new _RunTrace(result, this.segmentLoader);

        let promise: any = this.loadTraceConfig(modelSetKey, traceConfigKey)
        // Prepare the trace config
            .then((traceConfig: GraphDbTraceConfigTuple) => {
                // Assign the trace config to _RunTrace class
                runTrace._traceConfig = traceConfig;
                // Prepossess some trace rules
                for (let rule of traceConfig.rules) {
                    rule.prepare();
                }

            })
            .then(() => {
                return this.itemKeyLoader.getSegmentKeys(modelSetKey, startVertexKey);
            })
            .then((startSegmentKeys: string[]) => {
                return runTrace.run(startVertexKey, startSegmentKeys);
            })
            .then(() => result);
        return promise;
    }
}

class _RunTrace {

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
            if (propVal == rule.propertyValue)
                return true;
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