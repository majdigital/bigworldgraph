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
        config:[],
        init:function(){
            //Main Function
            this.config = [
                {
                    "has":{
                        "group":1
                    },
                    "type":"position",
                    "x":0.2,
                    "y":0.2,
                    "weight":0.7
                },
                {
                    "has":{
                        "group":2
                    },
                    "type":"position",
                    "x":0.8,
                    "y":0.2,
                    "weight":0.7
                },
                {
                    "has":{
                        "group":3
                    },
                    "type":"position",
                    "x":0.2,
                    "y":0.5,
                    "weight":0.7
                },
                {
                    "has":{
                        "group":4
                    },
                    "type":"position",
                    "x":0.8,
                    "y":0.5,
                    "weight":0.7
                },
                {
                    "has":{
                        "group":5
                    },
                    "type":"position",
                    "x":0.2,
                    "y":0.8,
                    "weight":0.7
                },
                {
                    "has":{
                        "group":8
                    },
                    "type":"position",
                    "x":0.8,
                    "y":0.8,
                    "weight":0.7
                }
            ]
            new this.Graph();
        }
    };

    BigWorldGraph.Graph = function(){
        var _this = this;
        _this.svg = d3.select('svg');
        _this.width = +_this.svg.attr('width');
        _this.height = +_this.svg.attr('height');
        _this.color = d3.scaleOrdinal(d3.schemeCategory20);
        _this.selected = {};
        _this.graph = {};
        _this.highlighted = null;
        _this.entry = "http://127.0.0.1:5000/";
        $.ajax({
            url:_this.entry,
            contentType: "text/plain",
            method:"GET",
            success:function(response){
                console.log(response);
            },
            error:function(xhr,err,msg){
                console.log(xhr);
                console.log(err);
                console.log(msg);
            }
        })


        /*d3.json(_this.entry, function(error,data){
            console.log(data)
            if(error)throw error;
            _this.graph.data = data;
            _this.buildGraph();
        });*/

        _this.buildGraph = function(){
            _this.graph.links = [];
            for(var id in _this.graph.data.nodes){
                var obj = _this.graph.data.nodes[id];

                obj.positionContraints = [];
                obj.linkStrength = 1;
                BigWorldGraph.config.forEach(function(confEntry){
                    for(var key in confEntry.has){
                        if(confEntry.has[key] !== obj[key]){
                            return true;
                        }
                    }
                    switch (confEntry.type){
                        case "position":
                            obj.positionContraints.push({
                                weight:confEntry.weight,
                                x:confEntry.x*_this.width,
                                y:confEntry.y*_this.height
                            });
                            break;
                    }
                });

            }
            for(var id in _this.graph.data.nodes){
                var obj = _this.graph.data.nodes[id];
                for(var depIndex in obj.depends){
                    var link = {
                        source : _this.graph.data.nodes[obj.depends[depIndex]],
                        target : obj
                    };
                    link.strength = (link.source.linkStrength || 1) * (link.target.linkStrength || 1);

                    _this.graph.links.push(link);
                }
            }
            var nodeValues = d3.values(_this.graph.data.nodes);
            console.log(_this.graph.links);

            var zoom = d3.zoom()
            .scaleExtent([1, 40])
            .translateExtent([[-100, -100], [_this.width + 90, _this.height + 100]])
            .on("zoom", _this.zoomed);

            _this.simulation = d3.forceSimulation(d3.values(_this.graph.data.nodes))
            .force("link",d3.forceLink().strength(0.5).id(function(d) { return d.id; }))
            .force('xPos', d3.forceX(_this.width/2).strength(0.2))
		    .force('yPos', d3.forceY(_this.height/2).strength(0.2))
            .force("collision",d3.forceCollide(40).strength(0.6))
            .force("center",d3.forceCenter(_this.width / 2, _this.height / 2));
            _this.svg.append("defs").selectAll("marker")
                .data(["default"])
                .enter().append("marker")
                .attr("id",function(d){ return d; })
                .attr("viewBox","0 -5 10 10")
                .attr("refX", 25)
                .attr("refY",-1.5)
                .attr("markerWidth",6)
                .attr("markerHeight",6)
                .attr("orient","auto")
                .append("path")
                .attr("d","M0,-5L10,0L0,5");

            _this.link = _this.svg.append("g")
                .attr("class","links")
                .selectAll("path")
                .data(_this.graph.links)
                .enter().append("path")
                .attr("marker-end","url(#default)")

            _this.nodes = _this.svg.append('g')
                .attr('class','nodes');


            _this.node = _this.nodes.selectAll('.node')
                .data(d3.values(_this.graph.data.nodes))
                .enter().append('g')
                .attr('class','node')
                .attr('x',function(d){
                    if(d.positionContraints[0]!=undefined){
                        return d.positionContraints[0].x;
                    }

                    return 0;
                })
                .attr('y',function(d){
                    if(d.positionContraints[0]!=undefined){
                        return d.positionContraints[0].y;
                    }

                    return 0;
                })
                .call(d3.drag()
                    .on("start",_this.dragstarted)
                    .on("drag",_this.dragged)
                    .on("end",_this.dragended))
                .on('mouseover',function(d){
                    if(!_this.selected.obj){
                        if(_this.mouseoutTimeout) {
                            clearTimeout(_this.mouseoutTimeout);
                            _this.mouseoutTimeout = null;
                        }
                        _this.highlightObject(d);
                    }
                })
                .on('mouseout',function(d){
                    if(!_this.selected.obj){
                        if(_this.mouseoutTimeout){
                            clearTimeout(_this.mouseoutTimeout);
                            _this.mouseoutTimeout = null;
                        }
                        _this.mouseoutTimeout = setTimeout(function(){
                            _this.highlightObject(null);
                        },300)
                    }
                });

            var nodeCircle = _this.node.append('circle')
                .attr('r',10)
                .attr('fill',function(d){
                    return _this.color(d.group);
                });

            var text = _this.svg.append("g")
                .selectAll("text")
                .data(d3.values(_this.graph.data.nodes))
                .enter().append("text")
                .attr("x",8)
                .attr("y",".31em")
                .text(function(d){ return d.id; });

            _this.simulation
                .nodes(d3.values(_this.graph.data.nodes))
                .on("tick", ticked);

            /*_this.simulation.force("link")
                .links(_this.graph.links).distance(function(d){
                    console.log(d.target.group*10);
                    return d.target.group*10;
                });*/
            _this.svg.call(zoom);
            function ticked(){
                text.attr("transform", transform);
                _this.link.attr("d", linkArc);

                //
                for(var id in _this.graph.data.nodes){
                    var obj = _this.graph.data.nodes[id];
                    obj.positionContraints.forEach(function(c){
                        var w = c.weight;
                        if(isNaN(c.x)) {
                            obj.x = (c.x * w + obj.x * (1-w));
                        }
                        if(isNaN(c.y)) {
                            obj.y = (c.y * w + obj.y * (1-w));
                        }
                    })
                };
                _this.node.attr("transform", transform);
            }
            function linkArc(d) {
              var dx = d.target.x - d.source.x,
                  dy = d.target.y - d.source.y,
                  dr = Math.sqrt(dx * dx + dy * dy);
              return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
          }
            function transform(d) {
                //console.log(d.x);
                return "translate(" + d.x + "," + d.y + ")";
            }
        };
        _this.zoomed = function(){
            console.log(d3.event);
            _this.nodes.attr('transform', d3.event.transform);
            _this.link.attr('transform',d3.event.transform);
        }
        _this.highlightObject = function(obj){
            if(obj){
                if(obj != _this.highlighted){
                    _this.node.classed('inactive',function(d){
                        console.log(obj.id);
                        console.log(obj !== d && d.depends.indexOf(obj.id) == -1 && d.dependedOnBy.indexOf(obj.id) == -1);
                        return (obj !== d && d.depends.indexOf(obj.id) == -1 && d.dependedOnBy.indexOf(obj.id) == -1);
                    });
                    _this.link.classed('inactive',function(d){
                        return (obj !== d.source && obj !== d.target);
                    });
                }
                _this.highlighted = obj;
            }else{
                if(_this.highlighted){
                    _this.node.classed('inactive',false);
                    _this.link.classed('inactive',false);
                }
                _this.highlighted = null;
            }
        }

        _this.dragstarted = function(d){
            /*if(!d3.event.active) _this.simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;*/
        };
        _this.dragged = function(d){
            /*d.fx = d3.event.x;
            d.fy = d3.event.y;*/
        };
        _this.dragended = function(d){
            /*if(!d3.event.active) _this.simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;*/
        };
    }
}());
