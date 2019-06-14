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
import {RunTrace} from "./PrivateRunTrace";

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
            .then(() => this.tupleService.offlineObserver.pollForTuples(ts, false))
            .then((tuples) => tuples[0]);
    }

    private runLocalTrace(modelSetKey: string, traceConfigKey: string,
                          startVertexKey: string): Promise<GraphDbTraceResultTuple> {

        let result = new GraphDbTraceResultTuple();
        result.modelSetKey = modelSetKey;
        result.traceConfigKey = traceConfigKey;
        result.startVertexKey = startVertexKey;


        let runTrace = new RunTrace(result, this.segmentLoader);

        let promise: any = this.loadTraceConfig(modelSetKey, traceConfigKey)
        // Prepare the trace config
            .then((traceConfig: GraphDbTraceConfigTuple) => {
                // Assign the trace config to RunTrace class
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
