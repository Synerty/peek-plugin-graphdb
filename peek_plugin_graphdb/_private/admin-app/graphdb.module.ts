import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {RouterModule, Routes} from "@angular/router";
import {EditSettingComponent} from "./edit-setting-table/edit.component";
import {StatusComponent} from "./status/status.component";
// Import our components
import {GraphDbComponent} from "./graphdb.component";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService
} from "@synerty/vortexjs";

import {
    graphDbActionProcessorName,
    graphDbFilt,
    graphDbObservableName,
    graphDbTupleOfflineServiceName
} from "@peek/peek_plugin_graphdb/_private";
// import {EditPropertyComponent} from "./edit-property-table/edit.component";
// import {EditSegmentTypeComponent} from "./edit-object-type-table/edit.component";
// import {ViewSegmentComponent} from "./view-segment/view-segment";


export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        graphDbActionProcessorName, graphDbFilt);
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        graphDbObservableName, graphDbFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(graphDbTupleOfflineServiceName);
}

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: '',
        component: GraphDbComponent
    }

];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule
    ],
    exports: [],
    providers: [
        TupleActionPushService, {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory
        },
        TupleOfflineStorageService, {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory
        },
        TupleDataObserverService, TupleDataOfflineObserverService, {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory
        },
    ],
    declarations: [GraphDbComponent,
        // ViewSegmentComponent,
        EditSettingComponent,
        StatusComponent
        // ,
        // EditPropertyComponent,
        // EditSegmentTypeComponent
    ]
})
export class GraphDbModule {

}
