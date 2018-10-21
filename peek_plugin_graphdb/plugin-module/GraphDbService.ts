import {Injectable} from "@angular/core";

import {
    ComponentLifecycleEventEmitter,
    Payload,
    TupleActionPushService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleSelector,
    VortexStatusService
} from "@synerty/vortexjs";

import {Subject} from "rxjs/Subject";
import {Observable} from "rxjs/Observable";
import {PrivateTracerService} from "./_private/tracer-service";
import {GraphDbTraceResultTuple} from "./GraphDbTraceResultTuple";
import {GraphDbLinkedModel} from "./GraphDbLinkedModel";
import {GraphDbTraceResultTuple} from "./_private";


// ----------------------------------------------------------------------------
/** LocationIndex Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage-old of the index
 *
 * 2) Return DispKey locations based on the index.
 *
 */
@Injectable()
export class GraphDbService extends ComponentLifecycleEventEmitter {

    constructor(private tracerService: PrivateTracerService) {
        super();


    }


    /** Get Trace Result
     *
     * Trace the graph with a pre-defined trace rule, and return a flat model
     *
     */
    getTraceResult(modelSetKey: string, traceConfigKey: string,
                   startVertexKey: string): Promise<GraphDbTraceResultTuple> {

        return this.tracerService
            .runTrace(modelSetKey, traceConfigKey, startVertexKey);
    }

    /** Get Trace Model
     *
     * Trace the graph with a pre-defined trace rule, and return a linked model
     *
     */
    getTraceModel(modelSetKey: string, traceConfigKey: string,
                  startVertexKey: string): Promise<GraphDbLinkedModel> {

        return this.tracerService
            .runTrace(modelSetKey, traceConfigKey, startVertexKey)
            .then((result: GraphDbTraceResultTuple) => {
                return GraphDbLinkedModel.createFromTraceResult(result);
            });

    }


}