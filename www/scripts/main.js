var BigWorldGraph = BigWorldGraph || {};
/*
::::::::::: ::::    ::: ::::::::::: :::::::::::
    :+:     :+:+:   :+:     :+:         :+:
    +:+     :+:+:+  +:+     +:+         +:+
    +#+     +#+ +:+ +#+     +#+         +#+
    +#+     +#+  +#+#+#     +#+         +#+
    #+#     #+#   #+#+#     #+#         #+#
########### ###    #### ###########     ###
*/
(function(){
    BigWorldGraph= {
        init:function(){
            //Main Function
            new this.Graph();
        }
    };

    BigWorldGraph.Graph = function(){
        console.log('Build a new Graph');
        var _this = this;
        _this.svg = d3.select('svg');
        _this.width = +_this.svg.attr('width');
        _this.height = +_this.svg.attr('height');
        _this.color = d3.scaleOrdinal(d3.schemeCategory20);
        _this.focus_node =
        _this.simulation = d3.forceSimulation()
        .force("link",d3.forceLink().id(function(d) { return d.id; }))
        .force("charge",d3.forceManyBody())
        .force("center",d3.forceCenter(_this.width / 2, _this.height / 2));

        d3.json("tempdata/relations.json", function(error,graph){
            if(error)throw error;
            var links = graph.links;
            _this.svg.append("defs").selectAll("marker")
                .data(["default"])
                .enter().append("marker")
                .attr("id",function(d){ return d; })
                .attr("viewBox","0 -5 10 10")
                .attr("refX", 15)
                .attr("refY",-1.5)
                .attr("markerWidth",6)
                .attr("markerHeight",6)
                .attr("orient","auto")
                .append("path")
                .attr("d","M0,-5L10,0L0,5");

            var link = _this.svg.append("g")
                .attr("class","links")
                .selectAll("path")
                .data(graph.links)
                .enter().append("path")
                .attr("marker-end","url(#default)")

            var node = _this.svg.append("g")
                .attr("class", "nodes")
                .selectAll("circle")
                .data(graph.nodes)
                .enter().append("circle")
                .attr("r",5)
                .attr("fill",function(d){return _this.color(d.group)})
                .call(d3.drag()
                    .on("start",_this.dragstarted)
                    .on("drag",_this.dragged)
                    .on("end",_this.dragended));

            node.on("mousedown",function(d){
                d3.event.stopPropagation();
                _this.onNodeOverHandler(d);
            });

            var text = _this.svg.append("g")
                .selectAll("text")
                .data(graph.nodes)
                .enter().append("text")
                .attr("x",8)
                .attr("y",".31em")
                .text(function(d){ return d.id; });

            _this.simulation
                .nodes(graph.nodes)
                .on("tick", ticked);

            _this.simulation.force("link")
                .links(graph.links);

            function ticked(){
                text.attr("transform", transform);
                link.attr("d", linkArc);

                node.attr("transform", transform);
            }
            function linkArc(d) {
              var dx = d.target.x - d.source.x,
                  dy = d.target.y - d.source.y,
                  dr = Math.sqrt(dx * dx + dy * dy);
              return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
            }
            function transform(d) {
                return "translate(" + d.x + "," + d.y + ")";
            }
        });

        _this.onNodeOverHandler = function(d){
            console.log(d);
        }

        _this.dragstarted = function(d){
            if(!d3.event.active) _this.simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        };
        _this.dragged = function(d){
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        };
        _this.dragended = function(d){
            if(!d3.event.active) _this.simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    }
}());
