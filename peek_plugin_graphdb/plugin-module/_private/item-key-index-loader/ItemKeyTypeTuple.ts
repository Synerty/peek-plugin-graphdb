import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";


@addTupleType
export class ItemKeyTypeTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "ItemKeyTypeTuple";

    //  A protected variable
    id__: number;

    //  The key of this ItemKeyType
    key: string;

    //  The key of the model set
    modelSetKey: string;

    //  The name of the ItemKeyType
    name: string;

    constructor() {
        super(ItemKeyTypeTuple.tupleName)
    }
}