import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";


@addTupleType
export class GraphDbEdgeTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbImportEdgeTuple";

    //  The unique key of this edge
    k: string;

    get key(): {} {
        return this.k;
    }

    //  The key of the source vertex
    sk: string;

    get srcVertexKey(): {} {
        return this.sk;
    }

    //  The key of the dest vertex
    dk: string;

    get dstVertexKey(): {} {
        return this.dk;
    }

    // The properties
    p: {} = {};

    get props(): {} {
        return this.p;
    }

    constructor() {
        super(GraphDbEdgeTuple.tupleName)
    }
}