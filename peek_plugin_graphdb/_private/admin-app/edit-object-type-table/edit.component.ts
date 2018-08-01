import {Component, OnInit} from "@angular/core";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
import {
    ComponentLifecycleEventEmitter,
    extend,
    TupleDataObserverService,
    TupleLoader,
    TupleSelector,
    VortexService
} from "@synerty/vortexjs";
import {graphDbFilt} from "@peek/peek_plugin_graphdb/_private";
import {GraphDbSegmentTypeTuple, GraphDbModelSetTuple} from "@peek/peek_plugin_graphdb";


@Component({
    selector: 'pl-graphdb-edit-object-type',
    templateUrl: './edit.component.html'
})
export class EditSegmentTypeComponent extends ComponentLifecycleEventEmitter {
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        "key": "admin.Edit.GraphDbSegmentTypeTuple"
    };

    items: GraphDbSegmentTypeTuple[] = [];

    loader: TupleLoader;
    modelSetById: { [id: number]: GraphDbModelSetTuple } = {};
    segmentTypeById: { [id: number]: GraphDbSegmentTypeTuple } = {};

    constructor(private balloonMsg: Ng2BalloonMsgService,
                vortexService: VortexService,
                private tupleObserver: TupleDataObserverService) {
        super();

        this.loader = vortexService.createTupleLoader(
            this, () => extend({}, this.filt, graphDbFilt)
        );

        this.loader.observable
            .subscribe((tuples: GraphDbSegmentTypeTuple[]) => this.items = tuples);

        // let modelSetTs = new TupleSelector(ModelSetTuple.tupleName, {});
        // this.tupleObserver.subscribeToTupleSelector(modelSetTs)
        //     .takeUntil(this.onDestroyEvent)
        //     .subscribe((tuples: ModelSetTuple[]) => {
        //         this.modelSetById = {};
        //         for (let tuple of tuples) {
        //             this.modelSetById[tuple.id] = tuple;
        //         }
        //     });
        //
        // let segmentTypeTs = new TupleSelector(GraphDbSegmentTypeTuple.tupleName, {});
        // this.tupleObserver.subscribeToTupleSelector(segmentTypeTs)
        //     .takeUntil(this.onDestroyEvent)
        //     .subscribe((tuples: GraphDbSegmentTypeTuple[]) => {
        //         this.segmentTypeById = {};
        //         for (let tuple of tuples) {
        //             this.segmentTypeById[tuple.id] = tuple;
        //         }
        //     });
    }

    modelSetTitle(tuple: GraphDbSegmentTypeTuple): string {
        // let modelSet = this.modelSetById[tuple.modelSetId];
        // return modelSet == null ? "" : modelSet.name;
        return "TODO";
    }

    segmentTypeTitle(tuple: GraphDbSegmentTypeTuple): string {
        // let segmentType = this.segmentTypeById[tuple.doc];
        // return segmentType == null ? "" : segmentType.name;
        return "TODO";
    }

    save() {
        this.loader.save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch(e => this.balloonMsg.showError(e));
    }

    resetClicked() {
        this.loader.load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch(e => this.balloonMsg.showError(e));
    }


}