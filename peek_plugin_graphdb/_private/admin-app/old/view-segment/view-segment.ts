// import {Component, OnInit} from "@angular/core";
// import {
//     ComponentLifecycleEventEmitter,
//     extend,
//     TupleLoader,
//     VortexService
// } from "@synerty/vortexjs";
// import {graphDbFilt} from "@peek/peek_plugin_graphdb/_private";
// import { SegmentTuple} from "@peek/peek_plugin_graphdb";
// import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";
//
//
// @Component({
//     selector: 'pl-graphdb-view-segment',
//     templateUrl: './view-segment.html'
// })
// export class ViewSegmentComponent extends ComponentLifecycleEventEmitter {
//     // This must match the dict defined in the admin_backend handler
//     private readonly filt = {
//         "key": "admin.Edit.GraphDbSegmentTuple"
//     };
//
//     docKey: string = '';
//     modelSetKey: string = '';
//
//     doc: SegmentTuple = new SegmentTuple();
//
//     loader: TupleLoader;
//
//     constructor(private balloonMsg: Ng2BalloonMsgService,
//                 vortexService: VortexService) {
//         super();
//
//         this.loader = vortexService.createTupleLoader(this,
//             () => extend({
//                 docKey: this.docKey,
//                 modelSetKey: this.modelSetKey
//             }, this.filt, graphDbFilt));
//
//         this.loader.observable
//             .subscribe((tuples: SegmentTuple[]) => {
//                 if (tuples.length == 0)
//                     this.doc = new SegmentTuple();
//                 else
//                     this.doc = tuples[0];
//             });
//     }
//
//     resetClicked() {
//         this.loader.load()
//             .then(() => this.balloonMsg.showSuccess("Reset Successful"))
//             .catch(e => this.balloonMsg.showError(e));
//     }
//
// }