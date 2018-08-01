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
import {SegmentResultI, PrivateSegmentLoaderService} from "./_private/segment-loader";
import {SegmentTuple} from "./SegmentTuple";
import {GraphDbTupleService} from "./_private";
import {GraphDbPropertyTuple} from "./GraphDbPropertyTuple";

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

    propertiesByName: { [key: string]: GraphDbPropertyTuple; } = {};

    constructor(private segmentLoader: PrivateSegmentLoaderService,
                private tupleService: GraphDbTupleService) {
        super();


        let propTs = new TupleSelector(GraphDbPropertyTuple.tupleName, {});
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(propTs)
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: GraphDbPropertyTuple[]) => {
                this.propertiesByName = {};

                for (let item of tuples) {
                    let propKey = this._makePropKey(item.modelSetId, item.name);
                    this.propertiesByName[propKey] = item;
                }
            });

    }

    private _makePropKey(modelSetId: number, name: string): string {
        return `${modelSetId}.${name.toLowerCase()}`;
    }


    /** Get Locations
     *
     * Get the objects with matching keywords from the index..
     *
     */
    getObjects(modelSetKey: string, keys: string[]): Promise<SegmentResultI> {
        return this.segmentLoader.getSegments(modelSetKey, keys);
    }

    getNiceOrderedProperties(doc: SegmentTuple): DocPropT[] {
        let props: DocPropT[] = [];

        for (let name of Object.keys(doc.segment)) {
            let propKey = this._makePropKey(doc.modelSet.id, name);
            let prop = this.propertiesByName[propKey] || new GraphDbPropertyTuple();
            props.push({
                title: prop.title,
                order: prop.order,
                value: doc.segment[name]
            });
        }
        props.sort((a, b) => a.order - b.order);

        return props;
    }

}