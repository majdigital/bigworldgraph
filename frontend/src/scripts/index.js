'use strict';

import '../styles/index.scss';

import 'whatwg-fetch'; // polyfill fetch

import Graph from './Graph';
import { dataloader } from './DataLoader';
import { loader, STATES } from './Loader';
import i18n from './config/i18n';
import fakeData from './fakeData.json';

class BigWorldGraph {
  constructor() {
    this.graph = null;
  }

  init(options = {}) {
    options = Object.assign({ locale: 'fr', fetchFakeData: false }, options);
    window.i18n = i18n(options.locale);

    loader.addListener(STATES.BUILDING_GRAPH, data =>
      this.onDataLoaded(data)
    );

    if (options.fetchFakeData) {
      console.warn(
        '⚠️Fake data is currently being loaded in order to minimize loading time on development'
      );
      loader.emit(STATES.BUILDING_GRAPH, fakeData);
    } else {
      const url = 'http://localhost:6050/entities';
      dataloader.loadData(url).then(response => {
        loader.emit(STATES.BUILDING_GRAPH, response);
      });
    }
  }

  onDataLoaded(data) {
    this.graph = new Graph(data);
  }
}

const bwg = new BigWorldGraph();

bwg.init({ fetchFakeData: true });
