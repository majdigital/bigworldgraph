'use strict';

import { categoriesColor } from './config/categories.js';

const wikipediaLogo = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 458.723 458.723"><path d="M455.724 93.489H364.32v15.613h9.143c7.145 0 13.588 3.667 17.237 9.81 3.648 6.143 3.786 13.555.368 19.829l-98.3 180.432-44.769-106.727 42.169-77.382a49.755 49.755 0 0 1 43.714-25.962h4.992V93.489H244.47v15.613h9.143c7.145 0 13.588 3.667 17.237 9.81 3.648 6.143 3.786 13.555.368 19.829l-30.587 56.143-27.259-64.984c-1.976-4.71-1.487-9.852 1.341-14.105s7.38-6.693 12.488-6.693h9.988V93.489H125.46v15.613h4.454a51.519 51.519 0 0 1 47.615 31.661l40.277 96.018-44.887 82.392L93.523 129.9c-1.976-4.71-1.487-9.852 1.341-14.105s7.38-6.693 12.488-6.693h13.737V93.489H0v15.613h10.064a51.517 51.517 0 0 1 47.615 31.661l91.526 218.191a10.23 10.23 0 0 0 9.458 6.282c3.804 0 7.163-1.998 8.986-5.344l11.939-21.91 45.582-83.646 43.884 104.617a10.23 10.23 0 0 0 9.458 6.282c3.804 0 7.163-1.998 8.986-5.344l11.939-21.91 110.58-202.919a49.755 49.755 0 0 1 43.714-25.962h4.992V93.487h-2.999v.002z"/></svg>';

export default class Details {
  constructor() {
    this.element = $('#details');
    this._isActive = false;
    this._isOpen = false;
    this._data = null;

    this.element.find('.openBtn').on('click', () => this.open());
    this.element.find('.closeBtn').on('click', () => this.close());
  }

  get contentContainer() {
    return this.element.find('.content');
  }

  get isOpen() {
    return this._isOpen;
  }

  set isOpen(value) {
    if (value) {
      this.element.addClass('is-open');
    } else {
      this.element.removeClass('is-open');
    }

    this._isOpen = value;
  }

  get isActive() {
    return this._isActive;
  }

  set isActive(value) {
    if (value) {
      this.element.addClass('is-active');
    } else {
      this.element.removeClass('is-active');
    }

    this._isActive = value;
  }

  get data() {
    return this._data;
  }

  set data(data) {
    if (data === this.data) return;
    this.isActive = !!data;
    this._data = data;
    this._updateContent();
  }

  _updateContent() {
    const { label, category, all } = this.data;

    const color = categoriesColor[category];
    const categoryLabel = i18n.categories[category];

    this.contentContainer.empty();
    let content = '';
    content += `<h2 style="color: ${color}"><span>${categoryLabel}</span></h2>`;
    content += `<h1><span>${label}</span></h1>`;

    if (all.senses.length) {
      content += `<section class="wikipedia">`;
      content += `<h3><span class="logo">${wikipediaLogo}</span>${i18n.wikipediaArticles}</h3>`

      all.senses.forEach(sense => {
        content += `<a data-wikipedia="${sense.wikidata_id}" href="" target="_blank" class="article">`;
        if (sense.claims.image) {
          content += `<img src="${sense.claims.image}"/>`;
          delete sense.claims.image;
        }
        content += '<div>';
        if (sense.label) content += `<h4>${sense.label}</h4>`;
        if (sense.description) content += `<h5>${sense.description}</h5>`;

        const claims = Object.entries(sense.claims);
        if (claims.length) {
          content += '<dl>';
          claims.forEach(([key, value]) => {
            content += `<dt>${key}</dt><dd>${value}</dd>`
          });
          content += '</dl>';
        }
        content += '</div>';
        content += '</a>';
      });
      content += `</section>`;
    }
    this.contentContainer.append(content);

    this.populateLinks();
  }

  populateLinks() {
    const articles = this.contentContainer.find('a');
    articles.each((index, article) => {
      const wikiId = article.getAttribute('data-wikipedia');
      this.getWikipediaLink(wikiId).then(url => article.setAttribute('href', url))
    })
  }

  getWikipediaLink(id) {
    return $.ajax({
      url: `https://www.wikidata.org/wiki/Special:EntityData/${id}.json`,
      method: 'GET',
      error: function(error) {
        console.error(error);
      },
    }).then(result => {
      const data = Object.values(result.entities)[0].sitelinks;
      if (data.frwiki) return data.frwiki.url;
      if (data.frwikinews) return data.frwikinews.url;
      if (data.enwiki) return data.enwiki.url;
      if (data.enwikinews) return data.enwikinews.url;
      return null;
    });
  }

  open() {
    this.isOpen = true;
  }

  close() {
    this.isOpen = false;
  }
}

export const details = new Details();
