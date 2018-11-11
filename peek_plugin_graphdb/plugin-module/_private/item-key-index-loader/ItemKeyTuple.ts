import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";
import {GraphDbModelSetTuple} from "../../GraphDbModelSetTuple";


@addTupleType
export class ItemKeyTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "ItemKeyTuple";

    //  The modelSetId for this itemKeyIndex.
    modelSet: GraphDbModelSetTuple = new GraphDbModelSetTuple();

    // The key of the vertex or edge
    itemKey: string;

    // This ItemKeyIndex Type ID
    itemType: number;
    static readonly ITEM_TYPE_VERTEX = 1;
    static readonly ITEM_TYPE_EDGE = 2;

    // The key of the segment where it's stored
    segmentKeys: string[];

    constructor() {
        super(ItemKeyTuple.tupleName)
    }

    static unpackJson(key: string, packedJson: string): ItemKeyTuple {
        // Reconstruct the data
        let objectProps: {} = JSON.parse(packedJson);

        // Get out the object type
        let thisModelSetId = objectProps['_msid'];
        delete objectProps['_msid'];

        // Create the new object
        let newSelf = new ItemKeyTuple();

        // These objects get replaced later in the UI
        newSelf.modelSet = new GraphDbModelSetTuple();
        newSelf.modelSet.id = thisModelSetId;

        // Unpack the custom data here
        newSelf.itemKey = key;
        newSelf.itemType = objectProps["itemType"];
        newSelf.segmentKeys = objectProps["segmentKeys"];

        return newSelf;

    }
}