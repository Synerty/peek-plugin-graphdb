 import {addTupleType, Tuple, TupleActionABC} from "@synerty/vortexjs";
import {graphdbTuplePrefix} from "../PluginNames";

@addTupleType
export class AddIntValueActionTuple extends TupleActionABC {
    static readonly tupleName = graphdbTuplePrefix + "AddIntValueActionTuple";

    stringIntId: number;
    offset: number;

    constructor() {
        super(AddIntValueActionTuple.tupleName)
    }
}