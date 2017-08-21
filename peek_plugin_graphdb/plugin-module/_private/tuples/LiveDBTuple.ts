import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphdbTuplePrefix} from "../PluginNames";


@addTupleType
export class LiveDBTuple extends Tuple {
    public static readonly tupleName = graphdbTuplePrefix + "LiveDBTuple";

    //  Description of date1
    dict1 : {};

    //  Description of array1
    array1 : any[];

    //  Description of date1
    date1 : Date;

    constructor() {
        super(LiveDBTuple.tupleName)
    }
}