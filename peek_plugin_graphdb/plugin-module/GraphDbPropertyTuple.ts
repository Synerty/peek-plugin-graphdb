import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";


@addTupleType
export class GraphDbPropertyTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbPropertyTuple";

    //  The id
    id: number;

    //  The modelSetId of the segment property
    modelSetId: number;

    //  The name of the segment property
    name: string;

    //  The title of the segment property
    title: string;

    //  The order of the segment property
    order: number;

    constructor() {
        super(GraphDbPropertyTuple.tupleName)
    }
}