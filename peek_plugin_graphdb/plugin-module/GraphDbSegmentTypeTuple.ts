import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";


@addTupleType
export class GraphDbSegmentTypeTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbSegmentTypeTuple";

    //  The id
    id: number;

    //  The modelSetId of the segment property
    modelSetId: number;

    //  The name of the segment type
    name: string;

    //  The title of the segment type
    title: string;

    constructor() {
        super(GraphDbSegmentTypeTuple.tupleName)
    }
}