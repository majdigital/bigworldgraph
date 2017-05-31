'use strict';
import Viva from "./vendor/vivagraphjs";

export default class Graph {
    constructor(graphData) {
        this.data = graphData;
        this.nodes = this.data.nodes;
        this.graph = void 0;
        this.renderer = void 0;
        this.graphics = void 0;
        this.links = this.createLinks();

        this.generateGraph();
    }

    createLinks(){
        var links = [];
        console.log(this.nodes);
        for(var node in this.nodes){
            console.log(this.nodes[node]);
            links.push(this.nodes[node]);
        }
        return links;
    }

    generateGraph(){
        this.graph = Viva.Graph.graph();
        this.graphics = Viva.Graph.View.svgGraphics(); 
        for(var node in this.nodes){
            this.graph.addNode(this.nodes[node].id);
            for(var i = 0; i<this.nodes[node].depends.length;i++){
                this.graph.addLink(this.nodes[node].id, this.nodes[node].depends[i]);
            }
        }


        this.renderer = Viva.Graph.View.renderer(this.graph,{
            container: document.getElementById('graphDiv'),
            graphics : this.graphics
        });

        this.renderer.run();
    }
}
