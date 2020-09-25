// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import App from './App';
import VeeValidate from 'vee-validate';
import BootstrapVue from 'bootstrap-vue';
import Snotify from 'vue-snotify';
import router from './router/router.js';
import { store } from './store/store.js';

import './../node_modules/jquery/dist/jquery.min.js';
import './../node_modules/bootstrap/dist/css/bootstrap.min.css';
import './../node_modules/bootstrap/dist/js/bootstrap.min.js';
import 'bootstrap-vue/dist/bootstrap-vue.css'
import 'vue-snotify/styles/simple.css';

import { library } from '@fortawesome/fontawesome-svg-core';
import { faUserCircle, faSyncAlt, faPlus, faTrashAlt, faPollH, faPenSquare, faArrowLeft, faSave } from '@fortawesome/free-solid-svg-icons';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faUserCircle, faSyncAlt, faPlus, faTrashAlt, faPollH, faPenSquare, faArrowLeft, faGithub, faSave);

Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.use(VeeValidate, { fieldsBagName: 'formFields' });
Vue.use(BootstrapVue);

Vue.use(Snotify, {
  toast: {
    timeout: 1500,
    showProgressBar: true,
    closeOnClick: true,
    pauseOnHover: false,
  },
})

Vue.config.productionTip = false;

// eslint-disable-next-line no-new
new Vue({
  router,
  store,
  el: '#app',
  render: h => h(App),
});
