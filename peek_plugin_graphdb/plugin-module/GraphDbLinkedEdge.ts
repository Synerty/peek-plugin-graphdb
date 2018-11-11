import {GraphDbLinkedVertex} from "./GraphDbLinkedVertex";


export class GraphDbLinkedEdge {

    //  The key of this edge
    key: string;

    //  The src vertex
    srcVertex: GraphDbLinkedVertex;

    //  The dst vertex
    dstVertex: GraphDbLinkedVertex;

    //  The properties of this edge
    props: {};

    getOtherVertex(vertexKey:string) : GraphDbLinkedVertex {
        if (this.srcVertex.key == vertexKey)
            return this.dstVertex;
        return this.srcVertex;
    }

}