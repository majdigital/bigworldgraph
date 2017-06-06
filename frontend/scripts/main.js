'use stric';

import {dataloader} from "./DataLoader";
import Graph from "./Graph";
import {loader} from "./Loader";
import Loader from "./Loader";

export default class BigWorldGraph {

    constructor(){
        this.url = "http://localhost";
        this.port = "8080";
        this.service = "tempdata/relations.json";
        this.graph = void 0;
        dataloader.LoadData(this.url+':'+this.port+'/'+this.service);
        loader.addListener(Loader.STATES.PREBUILDING_GRAPH, this.onChange.bind(this));
    }
    onChange(data){
        this.graph = new Graph(data);
    }
    createGraph(data){
        this.graph = new Graph(data);
    }
}


new BigWorldGraph();
