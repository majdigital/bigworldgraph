'use strict';
import './vendor/vivagraphjs';
import { loader, STATES } from './Loader';
import { details } from './Details';
import { settings } from './Settings';

import categories, { categoriesColor } from './config/categories';

export default class Graph {
  constructor(graphData) {
    this.data = graphData;
    this.nodes = this.data._items[0].nodes;
    this.graph = void 0;
    this.renderer = void 0;
    this.graphics = void 0;
    this.links = this.data._items[0].links;

    this.generateGraph();
    const data = categories.map(slug => ({
      slug,
      color: categoriesColor[slug],
      label: i18n.categories[slug],
    }));
    settings.populate(data);

    settings.addListener('reset', this.resetNodes.bind(this));
    settings.addListener('filter', this.filterNodes.bind(this));
    loader.addListener(STATES.DONE, () => {
      loader.hide();
      settings.on();
      this.renderGraph();
      setTimeout(() => this.pauseGraph(), 0);
    });
  }

  generateGraph() {
    this.graph = Viva.Graph.graph();
    this.layout = Viva.Graph.Layout.forceDirected(this.graph, {
      springLength: 50,
      springCoeff: 0.00008,
      dragCoeff: 0.01,
      gravity: -1.2,
      theta: 1,
    });
    this.graphics = Viva.Graph.View.svgGraphics();
    for (var node in this.nodes) {
      // console.log(this.nodes[node]);
      this.graph.addNode(this.nodes[node].uid, {
        label: this.nodes[node].label,
        category: this.nodes[node].category,
        all: this.nodes[node].data,
      });
    }

    for (var link in this.links) {
      this.graph.addLink(this.links[link].source, this.links[link].target);
    }

    this.graphics
      .node(node => {
        var randColor = this.getNodeColor(node);
        var ui = Viva.Graph.svg('g')
            .attr('class', 'nodeGroup')
            .attr('data-category', node.data.category),
          circle = Viva.Graph.svg('circle')
            .attr('r', '5px')
            .attr('cy', '12px')
            .attr('cx', '12px')
            .attr('stroke', randColor)
            .attr('stroke-width', '2px'),
          svgText = Viva.Graph.svg('text')
            .attr('y', '-4px')
            .text(node.data.label)
            .attr('class', 'text');

        ui.append(circle);
        ui.append(svgText);

        circle.addEventListener('mouseenter', () => {
          this.highlightRelated(node.id, true);
        });
        circle.addEventListener('mouseout', () => {
          this.highlightRelated(node.id, false);
        });
        circle.addEventListener('click', () => {
          this.nodeClicked(node.id);
        });
        return ui;
      })
      .placeNode(function(nodeUI, pos) {
        const x = pos.x - 24 / 2;
        const y = pos.y - 24 / 2;
        nodeUI.attr('transform', `translate(${x}, ${y})`);
      });

    this.graphics
      .link(function(link) {
        //console.log(link);
        var ui = Viva.Graph.svg('line')
          .attr('stroke', '#FFFFFF')
          .attr('class', 'link');
        return ui;
      })
      .placeLink(function(linkUI, fromPos, toPos) {
        linkUI
          .attr('x1', fromPos.x)
          .attr('x2', toPos.x)
          .attr('y1', fromPos.y)
          .attr('y2', toPos.y);
      });

    this.renderer = Viva.Graph.View.renderer(this.graph, {
      layout: this.layout,
      container: document.getElementById('graphDiv'),
      graphics: this.graphics,
      prerender: false,
    });

    // console.log('Run Precompute');

    this.precompute(500, () => this.renderGraph());

    // setTimeout(() => {
    //   console.log('pause');
    //   this.renderer.pause();
    // }, 1000);
  }

  precompute(iterations, cb) {
    var i = 0;
    // console.log('precompute');
    while (iterations > 0 && i < 10) {
      this.layout.step();
      iterations--;
      i++;
    }

    if (iterations > 0) {
      setTimeout(() => {
        this.precompute(iterations, cb);
      }, 0);
    } else {
      loader.emit(STATES.DONE, this);
      if (cb) { cb(); }
    }
  }

  renderGraph() {
    this.renderer.run();
  }

  pauseGraph() {
    this.renderer.pause();
  }

  highlightRelated(nodeId, isOn) {
    var nodeUI = this.graphics.getNodeUI(nodeId);
    if (nodeUI) {
      nodeUI.classList.remove(isOn ? 'off' : 'on');
      nodeUI.classList.add(isOn ? 'on' : 'off');
    }

    this.graph.forEachLinkedNode(nodeId, (node, link) => {
      var linkUI = this.graphics.getLinkUI(link.id);
      if (linkUI) {
        linkUI.classList.remove(isOn ? 'off': 'on');
        linkUI.classList.add(isOn ? 'on': 'off');
      }
    });
  }

  nodeClicked(nodeId) {
    // console.log('node clicked', nodeId);
    const toKeep = this.getLinkedNodes(nodeId);
    // var linksToKeep = this.getLinks(nodeId);
    const node = this.graph.getNode(nodeId);
    toKeep.push(node);

    this.graph.forEachNode(node => {
      const nodeUi = this.graphics.getNodeUI(node.id);
      nodeUi.setAttribute('fill', '#000000');
      nodeUi.classList.remove('active');
      // $(nodeUi).removeClass('hide active').addClass('hide');
    });

    // toKeep.map((item, index) => {
    //     let nodeUi = this.graphics.getNodeUI(item.id);
    //     $(nodeUi).removeClass('hide').addClass('show');
    // });

    // this.graph.forEachLink(link => {
    //     let linkUi = this.graphics.getLinkUI(link.id);
    //     $(linkUi).addClass('hide');
    // });
    // linksToKeep.map((item, index) => {
    //     let linkUi = this.graphics.getLinkUI(item.id);
    //     $(linkUi).removeClass('hide').addClass('show');
    // });

    // let pos = this.layout.getNodePosition(nodeId);
    // this.renderer.moveTo(pos.x, pos.y);

    const nodeUi = this.graphics.getNodeUI(nodeId);
    nodeUi.setAttribute('fill', this.getNodeColor(node));
    nodeUi.classList.add('active');

    details.data = node.data;
    // this.renderer.resume();

    // setTimeout(() => {
    //     this.renderer.pause();
    // },2000);
  }

  updateDetails(data) {
    details.update(data);
  }

  filterNodes(data) {
    const newCat = data.cat;

    const toKeep = this.getCategoryNodes(newCat);

    this.graph.forEachNode(node => {
      const nodeUi = this.graphics.getNodeUI(node.id);
      nodeUi.setAttribute('fill', '#000000');
      nodeUi.classList.remove('active');
      nodeUi.classList.add('hide');
    });
    toKeep.map((item, index) => {
      const nodeUi = this.graphics.getNodeUI(item.id);
      nodeUi.classList.remove('hide');
      nodeUi.classList.add('show');
    });

    this.graph.forEachLink(link => {
      const linkUi = this.graphics.getLinkUI(link.id);
      linkUi.classList.add('hide');
    });

    this.renderer.resume();

    // setTimeout(() => {
    //     this.renderer.pause();
    // },2000);
  }

  resetNodes() {
    this.graph.forEachNode(node => {
      const nodeUi = this.graphics.getNodeUI(node.id);
      nodeUi.attr('fill', '#000000');
      nodeUi.classList.remove('hide', 'active');
    });
    this.graph.forEachLink(link => {
      const linkUi = this.graphics.getLinkUI(link.id);
      linkUi.classList.remove('hide');
    });
    settings.close();
    this.renderer.moveTo(0, 0);
    this.renderer.resume();

    details.element.classList.remove('on', 'open');
    details.state = false;

    setTimeout(() => {
      this.renderer.pause();
    }, 5000);
  }

  getLinkedNodes(nodeId) {
    var nodes = [];
    this.graph.forEachLinkedNode(nodeId, function(node, link) {
      nodes.push(node);
    });
    return nodes;
  }

  getCategoryNodes(cat) {
    var nodes = [];
    var _cat = cat;

    this.graph.forEachNode(function(node, link) {
      //console.log(node.data.category);
      if (node.data.category == _cat) {
        nodes.push(node);
      }
    });

    return nodes;
  }

  getLinks(nodeId) {
    var links = [];
    this.graph.forEachLinkedNode(nodeId, function(node, link) {
      links.push(link);
    });
    return links;
  }

  getNodeColor(node) {
    return categoriesColor[node.data.category] || '#FFFFFF';
  }
}
