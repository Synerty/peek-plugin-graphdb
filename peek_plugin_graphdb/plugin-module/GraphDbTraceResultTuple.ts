import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";
import {GraphDbModelSetTuple} from "./GraphDbModelSetTuple";
import {GraphDbEdgeTuple} from "./GraphDbEdgeTuple";
import {GraphDbVertexTuple} from "./GraphDbVertexTuple";
import {GraphDbSegmentLinkTuple} from "./GraphDbSegmentLinkTuple";


@addTupleType
export class GraphDbTraceResultTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbTraceResultTuple";

    //  The key of the model set that the resuslt was created with.
    modelSetKey: string;

    //  The key of the Trace Config
    traceConfigKey: string;

    //  The key of the vertex start point of this trace
    startVertexKey: string;

    //  The edges
    edges: GraphDbEdgeTuple[];

    //  The vertexes
    vertexes: GraphDbVertexTuple[];

    constructor() {
        super(GraphDbTraceResultTuple.tupleName)
    }
}