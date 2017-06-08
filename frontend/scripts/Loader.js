'use strict';
import {settingslayer} from './SettingsLayer';
const STATES = {
    FETCHING_DATA : 'fetching',
    PREBUILDING_GRAPH : 'prebuilding',
    DONE : 'done',
    IDDLE : 'iddle'
}
let isFunction = function(obj){
    return typeof obj == 'function' || false;
}
let DOMElement = $('#loader');
export default class Loader {

    constructor() {

        this.currentState = Loader.STATES.IDDLE;
        this.listeners = new Map();
        DOMElement = $('#loader');


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
        Loader.changeState(label);


        if(listeners && listeners.length){
            listeners.forEach((listener) => {
                listener(...args);
            });
            return true;
        }
        return false;
    }
    static get STATES(){
        return STATES;
    }
    static changeState(newState){
        console.log('Change to new state:',newState);
        for(var state in Loader.STATES){
            if(Loader.STATES[state] == newState){
                console.log('Change State');
                this.currentState = newState;
                DOMElement.find('.label').text(this.currentState);
            }
        }
    }

    hide(){
        DOMElement.addClass('done');
        $('.logo').addClass('loaded');
        settingslayer.On();
    }
}

export const loader = new Loader();
