import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";

/** GraphDB Trace Result Edge Tuple
 *
 * This tuple contains the result of running a trace on the model
 *
 */
@addTupleType
export class GraphDbTraceResultEdgeTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "GraphDbTraceResultEdgeTuple";

    //  The key of this edge
    key: string;

    //  The key of the Trace Config
    srcVertexKey: string;

    //  The key of the vertex start point of this trace
    dstVertexKey: string;

    //  The edges
    props: {};

    constructor() {
        super(GraphDbTraceResultEdgeTuple.tupleName)
    }
}