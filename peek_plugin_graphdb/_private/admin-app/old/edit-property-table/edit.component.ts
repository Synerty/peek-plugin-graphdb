// import {Component, OnInit} from "@angular/core";
// import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
// import {
//     ComponentLifecycleEventEmitter,
//     extend,
//     TupleDataObserverService,
//     TupleLoader,
//     TupleSelector,
//     VortexService
// } from "@synerty/vortexjs";
// import {GraphDbModelSetTuple, GraphDbPropertyTuple} from "@peek/peek_plugin_graphdb";
// import {graphDbFilt} from "@peek/peek_plugin_graphdb/_private";
//
//
// @Component({
//     selector: 'pl-graphdb-edit-property',
//     templateUrl: './edit.component.html'
// })
// export class EditPropertyComponent extends ComponentLifecycleEventEmitter {
//     // This must match the dict defined in the admin_backend handler
//     private readonly filt = {
//         "key": "admin.Edit.GraphDbPropertyTuple"
//     };
//
//     items: GraphDbPropertyTuple[] = [];
//
//     loader: TupleLoader;
//     modelSetById: { [key: number]: GraphDbModelSetTuple } = {};
//
//     constructor(private balloonMsg: Ng2BalloonMsgService,
//                 vortexService: VortexService,
//                 private tupleObserver: TupleDataObserverService) {
//         super();
//
//         this.loader = vortexService.createTupleLoader(
//             this, () => extend({}, this.filt, graphDbFilt)
//         );
//
//         this.loader.observable
//             .subscribe((tuples: GraphDbPropertyTuple[]) => this.items = tuples);
//
//         let ts = new TupleSelector(GraphDbModelSetTuple.tupleName, {});
//         this.tupleObserver.subscribeToTupleSelector(ts)
//             .takeUntil(this.onDestroyEvent)
//             .subscribe((tuples: GraphDbModelSetTuple[]) => {
//                 this.modelSetById = {};
//                 for (let tuple of tuples) {
//                     this.modelSetById[tuple.id] = tuple;
//                 }
//             });
//     }
//
//     modelSetTitle(tuple: GraphDbPropertyTuple): string {
//         let modelSet = this.modelSetById[tuple.modelSetId];
//         return modelSet == null ? "" : modelSet.name;
//     }
//
//     save() {
//         this.loader.save()
//             .then(() => this.balloonMsg.showSuccess("Save Successful"))
//             .catch(e => this.balloonMsg.showError(e));
//     }
//
//     resetClicked() {
//         this.loader.load()
//             .then(() => this.balloonMsg.showSuccess("Reset Successful"))
//             .catch(e => this.balloonMsg.showError(e));
//     }
//
//
// }