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
        this.colors = ["#ed145b","#94bf8a","#5674b9","#47b5c6","#efcf2d"];

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
        var _this = this;
        this.graph = Viva.Graph.graph();
        this.graphics = Viva.Graph.View.svgGraphics();
        this.graphics.node(function(node){
            var ui = Viva.Graph.svg('g'),
                randColor = Math.floor(Math.random()*(5-0))+0,
                circle = Viva.Graph.svg('circle').attr('r','10px').attr('cy','10px').attr('cx','10px').attr('stroke',_this.colors[randColor]).attr('stroke-width','2px'),
                svgText = Viva.Graph.svg('text').attr('y', '-4px').text(node.id);

            ui.append(circle);
            ui.append(svgText);
            return ui;
        }).placeNode(function(nodeUI,pos){
            nodeUI.attr('transform',
                        'translate(' +
                              (pos.x - 24/2) + ',' + (pos.y - 24/2) +
                        ')');
        });
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

        setTimeout(function(){
            _this.renderer.pause();
        },10000)
    }
}
