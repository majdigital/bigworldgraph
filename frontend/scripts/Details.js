'use strict';
import IScroll from './vendor/iscroll-probe';

export default class Details {
  constructor() {
    console.log('IScroll');
    this.state = false;
    var iscrollEl = $('.scrollable')[0];
    this.scroll = new IScroll(iscrollEl, {
      mouseWheel: true,
    });
    this.element = $('#details');
    this.contentContainer = this.element.find('.scrollpane');
    this.currentData = void 0;
    this.previousData = void 0;

    this.openBtn = this.element.find('.pull');
    this.closeBtn = this.element.find('.closeBtn');

    this.openBtn.on('click', () => {
      this.open(this.currentData);
    });
    this.closeBtn.on('click', this.close.bind(this));
  }

  open(data) {
    this.state = true;
    setTimeout(() => {
      this.element.addClass('open');
    }, 100);

    if (this.currentData != this.previousData) {
      if (data.category == 'Politician') {
        this.showPolitician(data);
      }
      this.previousData = this.currentData;
    }

    setTimeout(() => {
      this.scroll.refresh();
    }, 500);
  }

  showPolitician(data) {
    if (!data.all.ambiguous) {
      this.contentContainer.empty();
      this.contentContainer.append(
        '<div class="content"><h2 class="' +
          data.category.toLowerCase() +
          '">' +
          data.category +
          '</h2><h1>' +
          data.label +
          '</h1><div class="image"><img src="' +
          data.all.senses[0].claims.image.target +
          '" alt="" /></div></div>'
      );
    }
  }

  close() {
    this.state = false;
    this.element.removeClass('open');
  }
}

export const details = new Details();
