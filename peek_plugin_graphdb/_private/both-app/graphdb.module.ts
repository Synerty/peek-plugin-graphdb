import {CommonModule} from "@angular/common";
import {NgModule} from "@angular/core";
import {Routes} from "@angular/router";
// Import a small abstraction library to switch between nativescript and web
import {PeekModuleFactory} from "@synerty/peek-util-web";
// Import the default route component
import {DocdbComponent} from "./graphdb.component";
// Import the required classes from VortexJS
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService
} from "@synerty/vortexjs";
// Import the names we need for the
import {
    graphDbFilt,
    graphDbObservableName,
    graphDbTupleOfflineServiceName,
    graphDbActionProcessorName
} from "@peek/peek_plugin_graphdb/_private/PluginNames";
// Import the names we need for the
import {ViewTraceComponent} from "./view-trace/view.component";

// Import the names we need for the



// Define the child routes for this plugin
export const pluginRoutes: Routes = [
    {
        path: 'view_trace',
        component: ViewTraceComponent
    },
    {
        path: 'view_trace/:modelSetKey/:traceConfigKey/:startVertexKey',
        component: ViewTraceComponent
    },
    {
        path: '',
        pathMatch: 'full',
        component: DocdbComponent
    }

];

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routs and then select the component to load.
@NgModule({
    imports: [
        CommonModule,
        PeekModuleFactory.RouterModule,
        PeekModuleFactory.RouterModule.forChild(pluginRoutes),
        ...PeekModuleFactory.FormsModules,
    ],
    exports: [],
    providers: [
    ],
    declarations: [DocdbComponent, ViewTraceComponent]
})
export class GraphDbModule {
}
