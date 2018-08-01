import {Component, Input} from "@angular/core";

import {ComponentLifecycleEventEmitter, TupleSelector} from "@synerty/vortexjs";
import {GraphDbTupleService, OfflineConfigTuple} from "@peek/peek_plugin_graphdb/_private";
import {
    PrivateSegmentLoaderService,
    PrivateSegmentLoaderStatusTuple
} from "@peek/peek_plugin_graphdb/_private/segment-loader";


@Component({
    selector: 'peek-plugin-graphdb-cfg',
    templateUrl: 'graphdb-cfg.component.web.html',
    moduleId: module.id
})
export class DocdbCfgComponent extends ComponentLifecycleEventEmitter {

    lastStatus: PrivateSegmentLoaderStatusTuple = new PrivateSegmentLoaderStatusTuple();

    offlineConfig: OfflineConfigTuple = new OfflineConfigTuple();

    private offlineTs = new TupleSelector(OfflineConfigTuple.tupleName, {});

    constructor(private segmentLoader: PrivateSegmentLoaderService,
                private tupleService: GraphDbTupleService) {
        super();

        this.lastStatus = this.segmentLoader.status();
        this.segmentLoader.statusObservable()
            .takeUntil(this.onDestroyEvent)
            .subscribe(value => this.lastStatus = value);

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(this.offlineTs, false, false, true)
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: OfflineConfigTuple[]) => {
                if (tuples.length == 0) {
                    this.tupleService.offlineObserver.updateOfflineState(
                        this.offlineTs, [this.offlineConfig]
                    );
                    return;
                }
            });

    }

    toggleOfflineMode(): void {
        this.offlineConfig.cacheChunksForOffline = !this.offlineConfig.cacheChunksForOffline;
        this.tupleService.offlineObserver.updateOfflineState(
            this.offlineTs, [this.offlineConfig]
        );
    }

}
