import {Component, Input, OnInit} from "@angular/core";
import {ActivatedRoute, Params} from "@angular/router";
import {graphDbBaseUrl} from "@peek/peek_plugin_graphdb/_private";
import {TitleService} from "@synerty/peek-util";

import {
    ComponentLifecycleEventEmitter,
    TupleActionPushService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleSelector,
    VortexStatusService
} from "@synerty/vortexjs";

import {
    GraphDbService,
    GraphDbTraceResultTuple
} from "@peek/peek_plugin_graphdb";
import {Observable} from "rxjs/Observable";
import {extend} from "@synerty/vortexjs/src/vortex/UtilMisc";


@Component({
    selector: 'plugin-graphdb-view-trace',
    templateUrl: 'view.component.web.html',
    moduleId: module.id
})
export class ViewTraceComponent extends ComponentLifecycleEventEmitter implements OnInit {

    modelSetKey: string = "pofGraph";
    traceConfigKey: string = "";
    startVertexKey: string = "";

    traceResult: GraphDbTraceResultTuple = null;

    error:string = '';

    constructor(private route: ActivatedRoute,
                private graphDbService: GraphDbService,
                private vortexStatus: VortexStatusService,
                private titleService: TitleService) {
        super();

        titleService.setTitle("DEV test trace ...");

    }

    ngOnInit() {

        this.route.params
            .takeUntil(this.onDestroyEvent)
            .subscribe((params: Params) => {
                let vars = {};

                if (typeof window !== 'undefined') {
                    window.location.href.replace(
                        /[?&]+([^=&]+)=([^&]*)/gi,
                        (m, key, value) => vars[key] = value
                    );
                }

                let key = params['key'] || vars['key'];
                // this.modelSetKey = params['modelSetKey'] || vars['modelSetKey'];
                // this.traceConfigKey = params['traceConfigKey'] || vars['traceConfigKey'];
                // this.startVertexKey = params['startVertexKey'] || vars['startVertexKey'];

                // this.runTrace();
            });

    }

    // private loadDoc(doc: SegmentTuple, key: string) {
    //     doc = doc || new SegmentTuple();
    //     this.doc = doc;
    //     this.docTypeName = '';
    //     this.docProps = [];
    //
    //     if (this.doc.key == null) {
    //         this.titleService.setTitle(`Segment ${key} Not Found`);
    //         return;
    //     }
    //
    //     this.titleService.setTitle(`Segment ${key}`);
    //
    //     this.docProps = this.graphDbService.getNiceOrderedProperties(this.doc);
    //     this.docTypeName = this.doc.segmentType.title;
    // }

    runTrace() {
        this.traceResult = null;
        this.error = '';

        this.graphDbService
            .runTrace(this.modelSetKey, this.traceConfigKey, this.startVertexKey)
            .then((result: GraphDbTraceResultTuple) => this.traceResult = result)
            .catch(e => this.error = e);
    }
}