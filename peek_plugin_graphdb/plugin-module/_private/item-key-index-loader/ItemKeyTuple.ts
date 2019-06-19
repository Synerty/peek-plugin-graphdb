import {addTupleType, Tuple} from "@synerty/vortexjs";
import {graphDbTuplePrefix} from "../PluginNames";


@addTupleType
export class ItemKeyTuple extends Tuple {
    public static readonly tupleName = graphDbTuplePrefix + "ItemKeyTuple";

    //  The model set of this itemKeyIndex
    modelSetKey: string;

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

    unpackJson(key: string, packedJson: string, modelSetKey: string): ItemKeyTuple {
        // Reconstruct the data
        let objectProps: {} = JSON.parse(packedJson);

        this.modelSetKey = modelSetKey;

        // Unpack the custom data here
        this.itemKey = key;
        this.itemType = objectProps["itemType"];
        this.segmentKeys = objectProps["segmentKeys"];

        return this;

    }
}