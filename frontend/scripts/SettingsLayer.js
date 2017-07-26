'use strict';

let isFunction = function(obj){
    return typeof obj == 'function' || false;
}
export default class SettingsLayer {
    constructor() {
        var _this = this;
        this.listeners = new Map();
        this.element = $('#infoInterface');
        this.state = false;
        this.openBtn = this.element.find('.pullup');
        this.categoriesContainer = this.element.find('.categories');
        this.resetBtn = this.element.find('.resetBtn');

        this.resetBtn.on('click',function(){
            _this.emit('reset');
        })

        this.openBtn.on('click',function(){
            if(_this.state){
                _this.Close();
            }else{
                _this.Open();
            }
        });
    }
    addListener(label,cb){
        this.listeners.has(label) || this.listeners.set(label, []);
        this.listeners.get(label).push(cb);
    }

    removeListener(label,cb){
        let listeners = this.listeners.get(label),
        index;

        if(listners && listeners.length){
            index = listeners.reduce((i,listeners,index) => {
                return (isFunction(listener) && listener === cb) ? i = index : i;
            },-1);

            if(index > -1){
                listeners.splice(index, 1);
                this.listeners.set(label,listeners);
                return true;
            }
        }

        return false;
    }
    emit(label, ...args){
        let listeners = this.listeners.get(label);


        if(listeners && listeners.length){
            listeners.forEach((listener) => {
                listener(...args);
            });
            return true;
        }
        return false;
    }

    Populate(data){
        console.log(data);
        var _this = this;
        data.forEach(function(cat){
            _this.categoriesContainer.append('<div class="category" data-cat="'+cat+'" ><div class="marker '+cat.toLowerCase()+'"></div><span>'+cat+'</span></div>');
        });
        var cats = _this.categoriesContainer.find('.category');
        cats.on('click',function(){
            var choosen = $(this).attr('data-cat');
            _this.emit('filter',{cat:choosen});
        })
    }

    Open(){
        this.state = true;
        this.element.addClass('open');
    }

    Close(){
        this.state = false;
        this.element.removeClass('open');
    }

    On(){
        this.element.addClass('on');
    }
}

export const settingslayer = new SettingsLayer();
