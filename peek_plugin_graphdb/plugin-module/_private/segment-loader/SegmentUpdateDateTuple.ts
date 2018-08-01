import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";


@addTupleType
export class SegmentUpdateDateTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "SegmentUpdateDateTuple";

    // Improve performance of the JSON serialisation
    protected _rawJonableFields = ['initialLoadComplete', 'updateDateByChunkKey'];

    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};

    constructor() {
        super(SegmentUpdateDateTuple.tupleName)
    }
}