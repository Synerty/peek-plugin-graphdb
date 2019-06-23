import {Component, OnInit} from "@angular/core";

let exampleDocMod = `
    {
        key: "ABC123",
        segment: {
        {
            alias:"A12345678COMP",
            name: "This is a circuit breaker ABC123",
            rating: "11kV"
        }
    }
`;

@Component({
    selector: 'graphdb-admin',
    templateUrl: 'graphdb.component.html'
})
export class GraphDbComponent implements OnInit {

    exampleDoc = exampleDocMod;

    ngOnInit() {

    }
}
