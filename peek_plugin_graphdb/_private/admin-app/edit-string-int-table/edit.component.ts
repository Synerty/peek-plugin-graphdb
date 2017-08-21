import {Component, OnInit} from "@angular/core";
import {
    extend,
    VortexService,
    ComponentLifecycleEventEmitter,
    TupleLoader
} from "@synerty/vortexjs";
import {StringIntTuple,
    graphdbFilt
} from "@peek/peek_plugin_graphdb/_private";


@Component({
    selector: 'pl-graphdb-edit-string-int',
    templateUrl: './edit.component.html'
})
export class EditStringIntComponent extends ComponentLifecycleEventEmitter {
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        "key": "admin.Edit.StringIntTuple"
    };

    items: StringIntTuple[] = [];
    itemsToDelete: StringIntTuple[] = [];

    loader: TupleLoader;

    constructor(vortexService: VortexService) {
        super();

        this.loader = vortexService.createTupleLoader(this,
            () => {
                let filt = extend({}, this.filt, graphdbFilt);
                // If we wanted to filter the data we get, we could add this
                // filt["lookupName"] = 'lookupType';
                return filt;
            });

        this.loader.observable
            .subscribe((tuples:StringIntTuple[]) => {
                this.items = tuples;
                this.itemsToDelete = [];
            });
    }

    addRow() {
        let t = new StringIntTuple();
        // Add any values needed for this list here, EG, for a lookup list you might add:
        // t.lookupName = this.lookupName;
        this.items.push(t);
    }

    removeRow(item) {
        if (item.id != null)
            this.itemsToDelete.push(item);

        let index: number = this.items.indexOf(item);
        if (index !== -1) {
            this.items.splice(index, 1);
        }
    }

    save() {
        let itemsToDelete = this.itemsToDelete;

        this.loader.save(this.items)
            .then(() => {
                if (itemsToDelete.length != 0) {
                    return this.loader.del(itemsToDelete);
                }
            });
    }

}