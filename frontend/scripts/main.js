'use stric';

import Graph from './Graph';
import { dataloader } from './DataLoader';
import Loader, { loader } from './Loader';
import i18n from './config/i18n';
import fakeData from '../assets/fakeData.json';

class BigWorldGraph {
  constructor() {
    this.graph = null;
  }

  init(locale, fetchFakeData = false) {
    window.i18n = i18n(locale);

    loader.addListener(Loader.STATES.PREBUILDING_GRAPH, data =>
      this.onDataLoaded(data)
    );

    if (fetchFakeData) {
      console.warn(
        '⚠️Fake data is currently being loaded in order to minimize loading time on development'
      );
      loader.emit(Loader.STATES.PREBUILDING_GRAPH, fakeData);
    } else {
      const url = 'http://localhost:6050/entities';
      dataloader.loadData(url).then(response => {
        loader.emit(Loader.STATES.PREBUILDING_GRAPH, response);
      });
    }
  }

  onDataLoaded(data) {
    this.graph = new Graph(data);
  }
}

const bwg = new BigWorldGraph();

bwg.init('fr', false);
