'use strict';

export const STATES = {
  FETCHING_DATA: 'fetching',
  BUILDING_GRAPH: 'building',
  DONE: 'done',
  IDDLE: 'iddle',
};

let isFunction = function(obj) {
  return typeof obj == 'function' || false;
};

export default class Loader {
  constructor() {
    this.element = $('#loader');
    this._state = STATES.IDDLE;
    this.listeners = new Map();
  }

  addListener(label, cb) {
    this.listeners.has(label) || this.listeners.set(label, []);
    this.listeners.get(label).push(cb);
  }

  removeListener(label, cb) {
    let listeners = this.listeners.get(label),
      index;

    if (listeners && listeners.length) {
      index = listeners.reduce((i, listeners, index) => {
        return isFunction(listener) && listener === cb ? (i = index) : i;
      }, -1);

      if (index > -1) {
        listeners.splice(index, 1);
        this.listeners.set(label, listeners);
        return true;
      }
    }

    return false;
  }

  emit(state, ...args) {
    let listeners = this.listeners.get(state);
    this.state = state;

    if (listeners && listeners.length) {
      listeners.forEach(listener => {
        listener(...args);
      });
      return true;
    }
    return false;
  }

  get state() {
    return this._state;
  }

  set state(value) {
    if (Object.values(STATES).includes(value)) {
      this._state = value;
      this.element.find('.label').text(i18n.loaderStates[value]);
    }
  }

  hide() {
    this.element.addClass('done');
    $('.app-logo').addClass('loaded');
  }
}

export const loader = new Loader();
