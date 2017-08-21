import {CommonModule} from "@angular/common";
import {FormsModule} from "@angular/forms";
import {NgModule} from "@angular/core";
import {Routes, RouterModule} from "@angular/router";
import {EditStringIntComponent} from "./edit-string-int-table/edit.component";
import {EditSettingComponent} from "./edit-setting-table/edit.component";


// Import our components
import {GraphDBComponent} from "./graphdb.component";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: '',
        component: GraphDBComponent
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
    providers: [],
    declarations: [GraphDBComponent, EditStringIntComponent, EditSettingComponent]
})
export class GraphDBModule {

}
