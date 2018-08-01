import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";


@addTupleType
export class PrivateSegmentLoaderStatusTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "PrivateSegmentLoaderStatusTuple";


    cacheForOfflineEnabled: boolean = false;
    initialLoadComplete: boolean = false;
    loadProgress: number = 0;
    loadTotal: number = 0;
    lastCheck: Date;

    constructor() {
        super(PrivateSegmentLoaderStatusTuple.tupleName)
    }
}
