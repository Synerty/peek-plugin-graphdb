import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";


@addTupleType
export class GraphDbSegmentLinkTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbSegmentLinkTuple";

    //  he key of the vertex that joins the two segments
    vertexKey: string;

    //  The segment that this segment links to
    segmentKey: string;

    constructor() {
        super(GraphDbSegmentLinkTuple.tupleName)
    }
}