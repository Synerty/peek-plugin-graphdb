import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";


@addTupleType
export class SegmentIndexUpdateDateTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "SegmentIndexUpdateDateTuple";

    // Improve performance of the JSON serialisation
    protected _rawJonableFields = ['initialLoadComplete', 'updateDateByChunkKey'];

    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};

    constructor() {
        super(SegmentIndexUpdateDateTuple.tupleName)
    }
}