import {Injectable} from "@angular/core";

import {
    ComponentLifecycleEventEmitter,
    TupleSelector,
    VortexService,
    VortexStatusService
} from "@synerty/vortexjs";

import {OfflineConfigTuple} from "../tuples/OfflineConfigTuple";
import {PrivateSegmentLoaderService} from "../segment-loader/PrivateSegmentLoaderService";
import {GraphDbTupleService} from "../GraphDbTupleService";
import {GraphDbTraceConfigTuple} from "../tuples/GraphDbTraceConfigTuple";
import {ItemKeyIndexLoaderService} from "../item-key-index-loader";
import {GraphDbTraceResultTuple} from "../../GraphDbTraceResultTuple";
import {PrivateRunTrace} from "./PrivateRunTrace";
import {GraphDbDoesKeyExistTuple} from "../../GraphDbDoesKeyExistTuple";

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
                    if (tuple.modelSetKey == modelSetKey
                        && tuple.key == traceConfigKey) {
                        return tuple;
                    }
                }
                return null;
            });
        return promise;
    }

    doesKeyExist(modelSetKey: string, vertexOrEdgeKey: string): Promise<boolean> {
        if (modelSetKey == null || modelSetKey.length == 0) {
            return Promise.reject("We've been passed a null/empty modelSetKey");
        }

        if (vertexOrEdgeKey == null || vertexOrEdgeKey.length == 0) {
            return Promise.reject("We've been passed a null/empty vertexOrEdgeKey");
        }


        if (!this.offlineConfig.cacheChunksForOffline
            || this.vortexStatusService.snapshot.isOnline) {
            return this.doesKeyExistServer(modelSetKey, vertexOrEdgeKey);
        }

        throw new Error("Peek must be online for tracing."
            + " Offline tracing is disabled in this release of Peek."
            + " Please contact Synerty for the latest release with offline tracing enabled.");
        // JJC TODO: Debug offline support
        // return this.doesKeyExistLocal(modelSetKey, vertexOrEdgeKey);

    }

    private async doesKeyExistServer(modelSetKey: string, vertexOrEdgeKey: string): Promise<boolean> {
        const ts = new TupleSelector(GraphDbDoesKeyExistTuple.tupleName, {
            "modelSetKey": modelSetKey,
            "vertexOrEdgeKey": vertexOrEdgeKey
        });

        if (!this.vortexStatusService.snapshot.isOnline) {
            await this.vortexStatusService.isOnline
                .filter(online => online)
                .first()
                .toPromise();
        }

        const tuples: GraphDbDoesKeyExistTuple[] = <any>await this.tupleService
            .offlineObserver.pollForTuples(ts, false);
        return tuples.length != 0 && tuples[0].exists;
    }


    private async doesKeyExistLocal(modelSetKey: string, vertexOrEdgeKey: string): Promise<boolean> {
        const keys = await this.itemKeyLoader.getSegmentKeys(modelSetKey, vertexOrEdgeKey);
        return keys.length != 0;
    }

    /** Get Segments
     *
     * Get the objects with matching keywords from the index..
     *
     */
    runTrace(modelSetKey: string, traceConfigKey: string,
             startVertexKey: string, maxVertexes: number | null = null): Promise<GraphDbTraceResultTuple> {

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
            return this.runServerTrace(modelSetKey, traceConfigKey,
                startVertexKey, maxVertexes);
        }

        throw new Error("Peek must be online for tracing."
            + " Offline tracing is disabled in this release of Peek."
            + " Please contact Synerty for the latest release with offline tracing enabled.");
        // JJC TODO: Debug offline support
        // return this.runLocalTrace(modelSetKey, traceConfigKey, startVertexKey, maxVertexes);
    }

    private runServerTrace(modelSetKey: string, traceConfigKey: string,
                           startVertexKey: string, maxVertexes: number): Promise<GraphDbTraceResultTuple> {

        let ts = new TupleSelector(GraphDbTraceResultTuple.tupleName, {
            "modelSetKey": modelSetKey,
            "traceConfigKey": traceConfigKey,
            "startVertexKey": startVertexKey,
            "maxVertexes": maxVertexes
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
                          startVertexKey: string, maxVertexes: number): Promise<GraphDbTraceResultTuple> {

        let result = new GraphDbTraceResultTuple();
        result.modelSetKey = modelSetKey;
        result.traceConfigKey = traceConfigKey;
        result.startVertexKey = startVertexKey;

        let traceConfigParam = null;

        let promise: any = this.loadTraceConfig(modelSetKey, traceConfigKey)
        // Prepare the trace config
            .then((traceConfig: GraphDbTraceConfigTuple) => {
                // Assign the trace config for the RunTrace class
                traceConfigParam = traceConfig;

                // Preprocess some trace rules
                for (let rule of traceConfig.rules) {
                    rule.prepare();
                }
            })
            .then(() => {
                return this.itemKeyLoader.getSegmentKeys(modelSetKey, startVertexKey);
            })
            .then((startSegmentKeys: string[]) => {
                const runTrace = new PrivateRunTrace(result, traceConfigParam,
                    this.segmentLoader, startVertexKey,
                    startSegmentKeys, maxVertexes);

                return runTrace.run();
            })
            .then(() => result);
        return promise;
    }
}
