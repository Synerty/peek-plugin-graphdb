import {Injectable} from "@angular/core";

import {ComponentLifecycleEventEmitter, TupleSelector} from "@synerty/vortexjs";
import {PrivateTracerService} from "./_private/tracer-service";
import {GraphDbTraceResultTuple} from "./GraphDbTraceResultTuple";
import {GraphDbLinkedModel} from "./GraphDbLinkedModel";
import {GraphDbTupleService} from "./_private";
import {GraphDbTraceConfigTuple} from "./_private/tuples/GraphDbTraceConfigTuple";
import {Observable} from "rxjs";


export interface TraceConfigListItemI {
    name: string;
    key: string;
}

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

    constructor(private tupleService: GraphDbTupleService,
                private tracerService: PrivateTracerService) {
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

    /** Trace Config List Items Observable
     *
     * Trace the graph with a pre-defined trace rule, and return a linked model
     *
     */
    traceConfigListItemsObservable(modelSetKey: string): Observable<TraceConfigListItemI[]> {

        const ts = new TupleSelector(GraphDbTraceConfigTuple.tupleName, {
            modelSetKey: modelSetKey
        });

        return this.tupleService
            .offlineObserver
            .subscribeToTupleSelector(ts)
            .map((tuples: GraphDbTraceConfigTuple[]) => {
                const out = [];
                for (let tuple of tuples) {
                    out.push({
                        name: tuple.name,
                        key: tuple.key
                    })
                }
                return out;
            });

    }


}