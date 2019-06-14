'use stric';

import Loader from './loader';
export default class DataLoader {
  constructor() {}

  loadData(endpoint, cb) {
    Loader.changeState(Loader.STATES.FETCHING_DATA);
    return $.ajax({
      url: endpoint,
      method: 'GET',
      contentType: 'text/plain',
      error: function(textStatus) {
        console.error(textStatus);
      },
    });
  }
}

export const dataloader = new DataLoader();
