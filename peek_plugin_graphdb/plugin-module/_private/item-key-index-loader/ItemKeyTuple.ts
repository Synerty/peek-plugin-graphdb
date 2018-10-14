import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "./_private/PluginNames";
import {ItemKeyTypeTuple} from "./ItemKeyTypeTuple";
import {GraphDbModelSetTuple} from "./GraphDbModelSetTuple";


@addTupleType
export class ItemKeyTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "ItemKeyTuple";

    //  The unique key of this itemKeyIndex
    key: string;

    //  The modelSetId for this itemKeyIndex.
    modelSet: GraphDbModelSetTuple = new GraphDbModelSetTuple();

    // This ItemKeyIndex Type ID
    itemKeyType: ItemKeyTypeTuple = new ItemKeyTypeTuple();

    // A string value of the itemKey
    valueStr: string;

    // An int value of the itemKey
    valueInt: number;

    // Add more values here

    constructor() {
        super(ItemKeyTuple.tupleName)
    }

    static unpackJson(key: string, packedJson: string): ItemKeyTuple {
        // Reconstruct the data
        let objectProps: {} = JSON.parse(packedJson);

        // Get out the object type
        let thisItemKeyTypeId = objectProps['_tid'];
        delete objectProps['_tid'];

        // Get out the object type
        let thisModelSetId = objectProps['_msid'];
        delete objectProps['_msid'];

        // Create the new object
        let newSelf = new ItemKeyTuple();

        newSelf.key = key;

        // These objects get replaced later in the UI
        newSelf.modelSet = new GraphDbModelSetTuple();
        newSelf.modelSet.id__ = thisModelSetId;
        newSelf.itemKeyType = new ItemKeyTypeTuple();
        newSelf.itemKeyType.id__ = thisItemKeyTypeId;

        // Unpack the custom data here
        newSelf.valueStr = objectProps["valueStr"];
        newSelf.valueInt = objectProps["valueInt"];

        return newSelf;

    }
}