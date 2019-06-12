'use strict';

let isFunction = function(obj) {
  return typeof obj == 'function' || false;
};

export default class Settings {
  constructor() {
    this.listeners = new Map();
    this.element = $('#settings');
    this.state = false;
    this.openBtn = this.element.find('.pullup');
    this.categoriesContainer = this.element.find('.categories');
    this.resetBtn = this.element.find('.resetBtn');

    this.resetBtn.on('click', () => {
      this.emit('reset');
    });

    this.openBtn.on('click', () => {
      if (this.state) {
        this.close();
      } else {
        this.open();
      }
    });
  }

  addListener(label, cb) {
    this.listeners.has(label) || this.listeners.set(label, []);
    this.listeners.get(label).push(cb);
  }

  removeListener(label, cb) {
    let listeners = this.listeners.get(label),
      index;

    if (listners && listeners.length) {
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

  emit(label, ...args) {
    let listeners = this.listeners.get(label);

    if (listeners && listeners.length) {
      listeners.forEach(listener => {
        listener(...args);
      });
      return true;
    }
    return false;
  }

  populate(data) {
    this.categoriesContainer.innerHTML = `<h2>${i18n.categories.label}</h2>`;
    data.forEach(category => {
      this.categoriesContainer.append(`
        <div class="category" data-category="${category.slug}">
            <div class="marker" style="background-color: ${
              category.color
            };"></div>
            <span>${category.label}</span>
        </div>`);
    });
    var cats = this.categoriesContainer.find('.category');
    cats.on('click', () => {
      var choosen = $(this).attr('data-category');
      this.emit('filter', { cat: choosen });
    });
  }

  open() {
    this.state = true;
    this.element.addClass('open');
  }

  close() {
    this.state = false;
    this.element.removeClass('open');
  }

  on() {
    this.element.addClass('on');
  }
}

export const settings = new Settings();
