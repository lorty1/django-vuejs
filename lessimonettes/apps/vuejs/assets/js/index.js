/**
 * Created by michael on 14/06/17.
 */
/**
 * First we will load all of this project's JavaScript dependencies which
 * include Vue and Vue Resource. This gives a great starting point for
 * building robust, powerful web applications using Vue and Laravel.
 */




import home from './components/home.vue';
import Vue from 'vue';

let vm = new Vue({
    el: '#app',
    
    components: {
        home,
    }
});
global.vm = vm