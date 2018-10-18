import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";
import {GraphDbModelSetTuple} from "./GraphDbModelSetTuple";
import {GraphDbEdgeTuple} from "./GraphDbEdgeTuple";
import {GraphDbVertexTuple} from "./GraphDbVertexTuple";
import {GraphDbSegmentLinkTuple} from "./GraphDbSegmentLinkTuple";


@addTupleType
export class GraphDbSegmentTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbLinkedSegment";

    //  The unique key of this segment
    key: string;

    //  The modelSetId for this segment.
    modelSet: GraphDbModelSetTuple;

    //  The edges
    edges: GraphDbEdgeTuple[];

    //  The vertexes
    vertexes: GraphDbVertexTuple[];

    //  The links to the other segments
    links: GraphDbSegmentLinkTuple[];


    constructor() {
        super(GraphDbSegmentTuple.tupleName)
    }
}