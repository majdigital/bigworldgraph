'use stric';

import { dataloader } from './DataLoader';
import Graph from './Graph';
import { loader } from './Loader';
import Loader from './Loader';

import i18n from './config/i18n';

export default class BigWorldGraph {
  constructor() {
    window.i18n = i18n('fr');

    this.url = 'http://localhost';
    this.port = '6050';
    this.service = 'entities';
    this.graph = void 0;
    dataloader.loadData(this.url + ':' + this.port + '/' + this.service);
    loader.addListener(
      Loader.STATES.PREBUILDING_GRAPH,
      this.onChange.bind(this)
    );
  }
  onChange(data) {
    this.graph = new Graph(data);
  }
  createGraph(data) {
    this.graph = new Graph(data);
  }
}

new BigWorldGraph();
