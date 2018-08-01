import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";


@addTupleType
export class GraphDbModelSetTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbModelSet";

    //  The unique key of this segment
    id: number;

    //  The unique key of this segment
    key: string;

    //  The unique key of this segment
    name: string;

    constructor() {
        super(GraphDbModelSetTuple.tupleName)
    }
}