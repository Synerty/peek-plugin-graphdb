import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";


@addTupleType
export class AdminStatusTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "AdminStatusTuple";

    segmentCompilerQueueStatus: boolean;
    segmentCompilerQueueSize: number;
    segmentCompilerQueueProcessedTotal: number;
    segmentCompilerQueueLastError: string;

    constructor() {
        super(AdminStatusTuple.tupleName)
    }
}