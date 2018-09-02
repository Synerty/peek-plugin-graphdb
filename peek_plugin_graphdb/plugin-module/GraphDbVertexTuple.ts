import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";
import {GraphDbModelSetTuple} from "./GraphDbModelSetTuple";


@addTupleType
export class GraphDbVertexTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbVertexTuple";

    //  The unique key of this edge
    k: string;

    get key(): {} {
        return this.k;
    }

    // The properties
    p: {} = {};

    get props(): {} {
        return this.p;
    }

    constructor() {
        super(GraphDbVertexTuple.tupleName)
    }
}