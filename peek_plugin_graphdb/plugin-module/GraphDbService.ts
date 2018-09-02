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
import {PrivateSegmentLoaderService, SegmentResultI} from "./_private/segment-loader";
import {GraphDbTupleService} from "./_private";

export interface DocPropT {
    title: string;
    value: string;
    order: number;
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

    constructor(private segmentLoader: PrivateSegmentLoaderService,
                private tupleService: GraphDbTupleService) {
        super();


    }


    /** Get Locations
     *
     * Get the objects with matching keywords from the index..
     *
     */
    getObjects(modelSetKey: string, keys: string[]): Promise<SegmentResultI> {
        return this.segmentLoader.getSegments(modelSetKey, keys);
    }


}