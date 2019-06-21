'use strict';

let isFunction = function(obj) {
  return typeof obj == 'function' || false;
};

export default class Settings {
  constructor() {
    this.listeners = new Map();
    this.element = document.getElementById('settings');
    this.state = false;
    this.openBtn = this.element.querySelector('.pullup');
    this.categoriesContainer = this.element.querySelector('.categories');
    this.resetBtn = this.element.querySelector('.resetBtn');

    this.resetBtn.addEventListener('click', () => {
      this.emit('reset');
    });

    this.openBtn.addEventListener('click', () => {
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
      this.categoriesContainer.innerHTML += `
        <div class="category" data-category="${category.slug}">
            <div class="marker" style="background-color: ${
              category.color
            };"></div>
            <span>${category.label}</span>
        </div>`;
    });
    var cats = this.categoriesContainer.querySelector('.category');
    cats.addEventListener('click', event => {
      const cat = event.target.getAttribute('data-category');
      this.emit('filter', { cat });
    });
  }

  open() {
    this.state = true;
    this.element.classList.add('open');
  }

  close() {
    this.state = false;
    this.element.classList.remove('open');
  }

  on() {
    this.element.classList.add('on');
  }
}

export const settings = new Settings();
