import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";
import {GraphDbSegmentTypeTuple} from "./GraphDbSegmentTypeTuple";
import {GraphDbModelSetTuple} from "./GraphDbModelSetTuple";


@addTupleType
export class SegmentTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "SegmentTuple";

    //  The unique key of this segment
    key: string;

    //  The modelSetId for this segment.
    modelSet: GraphDbModelSetTuple = new GraphDbModelSetTuple();

    // This Segment Type ID
    segmentType: GraphDbSegmentTypeTuple = new GraphDbSegmentTypeTuple();

    // The segment data
    segment: {} = {};

    constructor() {
        super(SegmentTuple.tupleName)
    }
}