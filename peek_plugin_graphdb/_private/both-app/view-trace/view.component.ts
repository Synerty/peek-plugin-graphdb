import {Component, Input, OnInit} from "@angular/core";
import {ActivatedRoute, Params} from "@angular/router";
import {graphDbBaseUrl} from "@peek/peek_plugin_graphdb/_private";
import {TitleService} from "@synerty/peek-util";
import {Ng2BalloonMsgService} from "@synerty/ng2-balloon-msg";

import {
    ComponentLifecycleEventEmitter,
    TupleActionPushService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleSelector,
    VortexStatusService
} from "@synerty/vortexjs";

import {GraphDbService, GraphDbTraceResultTuple} from "@peek/peek_plugin_graphdb";
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

    error: string = '';

    constructor(private balloonMsg: Ng2BalloonMsgService,
                private route: ActivatedRoute,
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


                this.modelSetKey = params['modelSetKey'] || vars['modelSetKey'];
                this.traceConfigKey = params['traceConfigKey'] || vars['traceConfigKey'];
                this.startVertexKey = params['startVertexKey'] || vars['startVertexKey'];

                if (!(this.modelSetKey && this.modelSetKey.length)) return;
                if (!(this.traceConfigKey && this.traceConfigKey.length)) return;
                if (!(this.startVertexKey && this.startVertexKey.length)) return;

                this.runTrace();
            });

    }

    // private loadDoc(doc: SegmentTuple, key: string) {
    //     this.itemKey = itemKey;
    //     this.itemKeyTypeName = '';
    //
    //     if (this.itemKey == null || this.itemKey.key == null) {
    //         this.balloonMsg.showWarning(`Failed to find ${key}`);
    //         this.titleService.setTitle(`ItemKey ${key} Not Found`);
    //         return;
    //     }
    //     this.balloonMsg.showSuccess(`We've found ${key}`);
    //
    //     this.titleService.setTitle(`ItemKey ${key}`);
    //
    //     this.itemKeyTypeName = this.itemKey.itemKeyType.name;
    // }

    runTrace() {
        this.traceResult = null;
        this.error = '';

        this.graphDbService
            .runTrace(this.modelSetKey, this.traceConfigKey, this.startVertexKey)
            .then((result: GraphDbTraceResultTuple) => this.traceResult = result)
            .catch(e => {
                this.balloonMsg.showError(e);
                this.error = e;
            });
    }
}