'use stric';
import { loader } from './Loader';
import Loader from './loader';
export default class DataLoader {
  constructor() {}

  loadData(endpoint, cb) {
    Loader.changeState(Loader.STATES.FETCHING_DATA);
    $.ajax({
      url: endpoint,
      method: 'GET',
      contentType: 'text/plain',
      success: function(response) {
        loader.emit(Loader.STATES.PREBUILDING_GRAPH, response);
      },
      error: function(textStatus) {
        console.error(textStatus);
      },
    });
  }
}

export const dataloader = new DataLoader();
