import Vue from 'vue';
import VueRouter from 'vue-router';

import CheckTasks from '../components/Body/CheckTasks/CheckTasks.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'home',
    component: CheckTasks,
  },
];

const router = new VueRouter({
  mode: 'history',
  routes: routes,
});

export default router;
