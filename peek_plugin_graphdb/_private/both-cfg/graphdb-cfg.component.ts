import { takeUntil } from "rxjs/operators";
import { Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { GraphDbTupleService } from "@peek/peek_plugin_graphdb/_private";
import {
    PrivateSegmentLoaderService,
    PrivateSegmentLoaderStatusTuple,
} from "@peek/peek_plugin_graphdb/_private/segment-loader";
import {
    ItemKeyIndexLoaderService,
    ItemKeyIndexLoaderStatusTuple,
} from "@peek/peek_plugin_graphdb/_private/item-key-index-loader";

@Component({
    selector: "peek-plugin-graphdb-cfg",
    templateUrl: "graphdb-cfg.component.web.html",
})
export class GraphDbCfgComponent extends NgLifeCycleEvents {
    segmentIndexStatus: PrivateSegmentLoaderStatusTuple =
        new PrivateSegmentLoaderStatusTuple();
    itemKeyIndexStatus: ItemKeyIndexLoaderStatusTuple =
        new ItemKeyIndexLoaderStatusTuple();

    constructor(
        private itemKeyIndexLoader: ItemKeyIndexLoaderService,
        private segmentLoader: PrivateSegmentLoaderService,
        private tupleService: GraphDbTupleService
    ) {
        super();

        this.segmentIndexStatus = this.segmentLoader.status();
        this.segmentLoader
            .statusObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => (this.segmentIndexStatus = value));

        this.itemKeyIndexStatus = this.itemKeyIndexLoader.status();
        this.itemKeyIndexLoader
            .statusObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => (this.itemKeyIndexStatus = value));
    }
}
