'use strict';
import Viva from "./vendor/vivagraphjs";
import {loader} from './Loader';
import Loader from './loader';
export default class Graph {
    constructor(graphData) {
        this.data = graphData;
        this.nodes = this.data._items[0].nodes;
        this.graph = void 0;
        this.renderer = void 0;
        this.graphics = void 0;
        this.links = this.data._items[0].links;
        this.colors = [
            {"Affair":"#bb1b66"},
            {"Politician":"#9565f1"},
            {"Party":"#6579f1"},
            {"Company":"#3db4ca"},
            {"Organization":"#56b57f"},
            {"Media":"#75b556"},
            {"Person":"#d2de4d"}
        ];
        this.categories = ["Affair","Politician","Party","Company","Organization","Media","Person"]

        this.generateGraph();
        loader.addListener(Loader.STATES.DONE, this.renderGraph.bind(this));
    }

    generateGraph(){
        var _this = this;
        this.graph = Viva.Graph.graph();
        this.layout = Viva.Graph.Layout.forceDirected(this.graph,{
            springLength : 50,
           springCoeff : 0.00008,
           dragCoeff : 0.01,
           gravity : -1.2,
           theta : 1
        });
        this.graphics = Viva.Graph.View.svgGraphics();
        for(var node in this.nodes){
            console.log(this.nodes[node]);
            this.graph.addNode(this.nodes[node].uid,{label:this.nodes[node].label, category:this.nodes[node].category,all:this.nodes[node].data});

        }

        for(var link in this.links){
            this.graph.addLink(this.links[link].source,this.links[link].target);
        }

        this.graphics.node(function(node){
            var randColor =  _this.getNodeColor(node);
            var ui = Viva.Graph.svg('g').attr('class','nodeGroup').attr('data-cat',node.data.category),
                circle = Viva.Graph.svg('circle').attr('r','5px').attr('cy','12px').attr('cx','12px').attr('stroke',randColor).attr('stroke-width','2px'),
                svgText = Viva.Graph.svg('text').attr('y', '-4px').text(node.data.label).attr('class','text');

            ui.append(circle);
            ui.append(svgText);

            $(circle).on('mouseenter',function(){
                _this.highlightRelated(node.id,true);
            });
            $(circle).on('mouseout',function(){
                _this.highlightRelated(node.id,false);
            });
            $(circle).on('click',function(){
                _this.nodeClicked(node.id);
            });
            return ui;
        }).placeNode(function(nodeUI,pos){
            nodeUI.attr('transform',
                        'translate(' +
                              (pos.x - 24/2) + ',' + (pos.y - 24/2) +
                        ')');
        });

        this.graphics.link(function(link){
            //console.log(link);
            var ui = Viva.Graph.svg('line').attr('stroke','#FFFFFF').attr('class','link');
            return ui;
        }).placeLink(function(linkUI, fromPos, toPos){
            linkUI.attr('x1',fromPos.x).attr('x2',toPos.x).attr('y1',fromPos.y).attr('y2',toPos.y);
        });




        this.renderer = Viva.Graph.View.renderer(this.graph,{
            layout:this.layout,
            container: document.getElementById('graphDiv'),
            graphics : this.graphics,
            prerender:false
        });

        //this.renderer.run();
        console.log('Run Precompute');

        this.precompute(500,this.renderGraph);


    }

    precompute(iterations, cb){
        var i = 0;
        var _this = this;
        console.log('precompute');
        while (iterations >0 && i < 10){
            _this.layout.step();
            iterations--;
            i++;
        }

        if(iterations > 0){
            setTimeout(function(){
                _this.precompute(iterations, cb);
            },0)
        }else{
            loader.emit(Loader.STATES.DONE, _this)

        }
    }

    renderGraph(context){
        loader.hide();
        setTimeout(function(){
            context.renderer.run();
        },3000);

        setTimeout(function(){
            context.renderer.pause();
        },8000)

    }

    highlightRelated(nodeId,isOn){
        var _this = this;
        var nodeUI = _this.graphics.getNodeUI(nodeId);
        if(nodeUI){
            isOn ? $(nodeUI).removeClass('off').addClass('on') :$(nodeUI).removeClass('on').addClass('off');
        }
        this.graph.forEachLinkedNode(nodeId,function(node, link){

            var linkUI = _this.graphics.getLinkUI(link.id);
            if(linkUI){
                isOn ? $(linkUI).removeClass('off').addClass('on') :$(linkUI).removeClass('on').addClass('off');
            }
        });
    }
    nodeClicked(nodeId){
        var _this = this;
        var toKeep = this.getLinkedNodes(nodeId);
        var linksToKeep = this.getLinks(nodeId);
        var node = this.graph.getNode(nodeId);
        toKeep.push(node);

        this.graph.forEachNode(function(node){
            let nodeUi = _this.graphics.getNodeUI(node.id);
            nodeUi.attr('fill','#000000');
            $(nodeUi).removeClass('hide active').addClass('hide');
        });
        toKeep.map((item, index) => {
            let nodeUi = _this.graphics.getNodeUI(item.id);
            $(nodeUi).removeClass('hide').addClass('show');
        });

        this.graph.forEachLink(function(link){
            let linkUi = _this.graphics.getLinkUI(link.id);
            $(linkUi).addClass('hide');
        });
        linksToKeep.map((item, index) => {
            let linkUi = _this.graphics.getLinkUI(item.id);
            $(linkUi).removeClass('hide').addClass('show');
        });

        let pos = _this.layout.getNodePosition(nodeId);
        _this.renderer.moveTo(pos.x, pos.y);

        let nodeUi = _this.graphics.getNodeUI(nodeId);
        nodeUi.attr('fill',_this.getNodeColor(_this.graph.getNode(nodeId)));
        $(nodeUi).addClass('active');

        _this.renderer.resume();

        setTimeout(function(){
            _this.renderer.pause();
        },2000)

    }

    getLinkedNodes(nodeId){
        var nodes = [];
        var _this = this;
        this.graph.forEachLinkedNode(nodeId,function(node,link){

            nodes.push(node);
        });
        return nodes;
    }
    getLinks(nodeId){
        var links = [];
        var _this = this;
        this.graph.forEachLinkedNode(nodeId,function(node,link){
            links.push(link);
        });
        return links;
    }
    getNodeColor(node){
        const colorIndex = this.categories.findIndex(category => node.data.category == category);
        const colorProp = this.categories.filter(category => node.data.category == category)
        return colorIndex >= 0 ? this.colors[colorIndex][colorProp[0]] : "#FFFFFF";

        /*for(var i = 0; i<this.categories.length;i++){
            console.log(this.categories[i]);
            if(node.data.category == this.categories[i]){
                console.log(this.colors[i])
                return this.colors[i];
            }else{
                return "#ffffff";
            }
        }*/
    }
}
