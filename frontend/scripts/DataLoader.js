'use stric';

import { loader, STATES } from './Loader';
export default class DataLoader {
  constructor() {}

  loadData(endpoint, cb) {
    loader.state = STATES.FETCHING_DATA;
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
