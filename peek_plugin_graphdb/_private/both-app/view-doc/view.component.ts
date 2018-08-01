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
    GraphDbSegmentTypeTuple,
    GraphDbPropertyTuple,
    GraphDbService,
    DocPropT,
    SegmentResultI,
    SegmentTuple
} from "@peek/peek_plugin_graphdb";
import {Observable} from "rxjs/Observable";
import {extend} from "@synerty/vortexjs/src/vortex/UtilMisc";


@Component({
    selector: 'plugin-graphDb-result',
    templateUrl: 'view.component.web.html',
    moduleId: module.id
})
export class ViewDocComponent extends ComponentLifecycleEventEmitter implements OnInit {

    doc: SegmentTuple = new SegmentTuple();
    docProps: DocPropT[] = [];
    docTypeName: string = '';

    constructor(private route: ActivatedRoute,
                private graphDbService: GraphDbService,
                private vortexStatus: VortexStatusService,
                private titleService: TitleService) {
        super();

        titleService.setTitle("Loading Segment ...");

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
                let modelSetKey = params['modelSetKey'] || vars['modelSetKey'];

                this.graphDbService.getObjects(modelSetKey, [key])
                    .then((docs: SegmentResultI) => this.loadDoc(docs[key], key));

            });

    }

    private loadDoc(doc: SegmentTuple, key: string) {
        doc = doc || new SegmentTuple();
        this.doc = doc;
        this.docTypeName = '';
        this.docProps = [];

        if (this.doc.key == null) {
            this.titleService.setTitle(`Segment ${key} Not Found`);
            return;
        }

        this.titleService.setTitle(`Segment ${key}`);

        this.docProps = this.graphDbService.getNiceOrderedProperties(this.doc);
        this.docTypeName = this.doc.segmentType.title;
    }


}