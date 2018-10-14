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
import {ItemKeyTypeTuple, GraphDbModelSetTuple} from "@peek/peek_plugin_graphdb";


@Component({
    selector: 'pl-graphdb-edit-item-key-type',
    templateUrl: './edit.component.html'
})
export class EditItemKeyTypeComponent extends ComponentLifecycleEventEmitter {
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        "key": "admin.Edit.ItemKeyType"
    };

    items: ItemKeyTypeTuple[] = [];

    loader: TupleLoader;
    modelSetById: { [id: number]: GraphDbModelSetTuple } = {};
    itemKeyTypeById: { [id: number]: ItemKeyTypeTuple } = {};

    constructor(private balloonMsg: Ng2BalloonMsgService,
                vortexService: VortexService,
                private tupleObserver: TupleDataObserverService) {
        super();

        this.loader = vortexService.createTupleLoader(
            this, () => extend({}, this.filt, graphDbFilt)
        );

        this.loader.observable
            .subscribe((tuples: ItemKeyTypeTuple[]) => this.items = tuples);

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
        // let itemKeyTypeTs = new TupleSelector(ItemKeyType.tupleName, {});
        // this.tupleObserver.subscribeToTupleSelector(itemKeyTypeTs)
        //     .takeUntil(this.onDestroyEvent)
        //     .subscribe((tuples: ItemKeyType[]) => {
        //         this.itemKeyTypeById = {};
        //         for (let tuple of tuples) {
        //             this.itemKeyTypeById[tuple.id] = tuple;
        //         }
        //     });
    }

    modelSetTitle(tuple: ItemKeyTypeTuple): string {
        // let modelSet = this.modelSetById[tuple.modelSetId];
        // return modelSet == null ? "" : modelSet.name;
        return "TODO";
    }

    itemKeyTypeTitle(tuple: ItemKeyTypeTuple): string {
        // let itemKeyType = this.itemKeyTypeById[tuple.itemKey];
        // return itemKeyType == null ? "" : itemKeyType.name;
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