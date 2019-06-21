'use strict';

import { loader, STATES } from './Loader';
export default class DataLoader {
  constructor() {}

  loadData(endpoint, cb) {
    loader.state = STATES.FETCHING_DATA;
    return fetch(endpoint)
      .catch(error => {
        console.error(error);
      })
      .then(response => {
        return response.json();
      });
  }
}

export const dataloader = new DataLoader();
