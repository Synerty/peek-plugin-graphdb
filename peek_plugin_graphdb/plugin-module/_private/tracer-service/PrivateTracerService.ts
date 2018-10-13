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
import {GraphDbTraceResultTuple} from "../../GraphDbTraceResultTuple";
import {PrivateSegmentLoaderService} from "../segment-loader/PrivateSegmentLoaderService";
import {GraphDbTupleService} from "../GraphDbTupleService";

// ----------------------------------------------------------------------------


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

        // let modelSetTs = new TupleSelector(GraphDbModelSetTuple.tupleName, {});
        // this.tupleService.offlineObserver
        //     .subscribeToTupleSelector(modelSetTs)
        //     .takeUntil(this.onDestroyEvent)
        //     .subscribe((tuples: GraphDbModelSetTuple[]) => {
        //         this.modelSetByIds = {};
        //         for (let item of tuples) {
        //             this.modelSetByIds[item.id] = item;
        //         }
        //         this._hasModelSetLoaded = true;
        //         this._notifyReady();
        //     });

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

        if (!this.offlineConfig.cacheChunksForOffline) {
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

        return Promise.reject("Local trace is not implemented");

    }
}