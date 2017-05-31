'use stric';

import {dataloader} from "./DataLoader";
import Graph from "./Graph";

export default class BigWorldGraph {

    constructor(){
        this.url = "http://localhost";
        this.port = "8080";
        this.service = "tempdata/relations.json";
        this.graph = void 0;
        dataloader.LoadData(this.url+':'+this.port+'/'+this.service, this.createGraph.bind(this));

    }

    createGraph(data){
        console.log(this);
        this.graph = new Graph(data); 
    }
}


new BigWorldGraph();
