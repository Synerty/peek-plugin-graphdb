import { Component } from "@angular/core"
import {
    NgLifeCycleEvents,
    TupleDataObserverService,
    TupleSelector
} from "@synerty/vortexjs"
import { ServerStatusTuple } from "@peek/peek_plugin_graphdb/_private"
import { BalloonMsgService } from "@synerty/peek-plugin-base-js"

@Component({
    selector: "pl-graphdb-status",
    templateUrl: "./status.component.html"
})
export class StatusComponent extends NgLifeCycleEvents {
    item: ServerStatusTuple = new ServerStatusTuple()
    
    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleObserver: TupleDataObserverService
    ) {
        super()
        
        let ts = new TupleSelector(ServerStatusTuple.tupleName, {})
        this.tupleObserver.subscribeToTupleSelector(ts)
            .takeUntil(this.onDestroyEvent)
            .subscribe((tuples: ServerStatusTuple[]) => {
                this.item = tuples[0]
            })
        
    }
    
}
