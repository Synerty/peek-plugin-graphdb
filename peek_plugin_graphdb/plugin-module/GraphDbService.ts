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


    /** Get Locations
     *
     * Get the objects with matching keywords from the index..
     *
     */
    runTrace(modelSetKey: string, traceConfigKey: string,
             startVertexKey: string): Promise<GraphDbTraceResultTuple> {

        return this.tracerService
            .runTrace(modelSetKey, traceConfigKey, startVertexKey);

    }


}