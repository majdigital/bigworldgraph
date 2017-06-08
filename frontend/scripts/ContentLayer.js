'use strict';
import IScroll from "./vendor/iscroll-probe";

export default class ContentLayer {
    constructor() {
        console.log('IScroll');
        this.state = false;
        var _this = this;
        var iscrollEl = $('.scrollable')[0];
        this.scroll = new IScroll(iscrollEl,{
            mouseWheel:true
        });
        this.element = $('#contentLayer');
        this.contentContainer = this.element.find('.scrollpane');
        this.currentData = void 0;

        this.openBtn = this.element.find('.pull');
        this.closeBtn = this.element.find('.closeBtn');

        this.openBtn.on('click',function(){
            _this.Open(_this.currentData);
        })
        this.closeBtn.on('click',_this.Close.bind(this));

    }

    Open(data) {
        this.state = true;
        this.element.addClass('open');
        var _this = this;
        if(data.category == 'Politician'){
            this.ShowPolitician(data);
        }

        setTimeout(function(){
            _this.scroll.refresh();
        },500);

    }

    ShowPolitician(data){
        if(!data.all.ambiguous){
            this.contentContainer.append('<div class="content"><h2 class="'+data.category.toLowerCase()+'">'+data.category+'</h2><h1>'+data.label+'</h1><div class="image"><img src="'+data.all.senses[0].claims.image.target+'" alt="" /></div></div>');
        }
    }

    Close(){
        this.state = false;
        this.element.removeClass('open');
    }
}

export const contentlayer = new ContentLayer()
