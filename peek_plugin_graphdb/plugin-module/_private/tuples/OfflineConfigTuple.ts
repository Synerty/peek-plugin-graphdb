import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";


@addTupleType
export class OfflineConfigTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "OfflineConfigTuple";

    cacheChunksForOffline: boolean = false;

    constructor() {
        super(OfflineConfigTuple.tupleName)
    }
}