import Vue from 'vue';
import Vuex from 'vuex';
import axios from '../axiosConf';
import AuthService from '../auth/AuthService';
import EventBus from '../event-bus.js';

Vue.use(Vuex);

export const store = new Vuex.Store({
  state: {
    checkTasks: [],
    authenticated: false,
    userEmail: null,
    mainTableBusy: true,
  },
  getters: {
    checkTasks: state => {
      return state.checkTasks;
    },
    mainTableBusy: state => {
      return state.mainTableBusy;
    },
    userAuthStatus: state => {
      return state.authenticated;
    },
    userEmail: state => {
      return state.userEmail;
    },
  },
  mutations: {
    changeAuthStatus (state, authStatus) {
      state.authenticated = authStatus;
    },
    setUserEmail (state, email) {
      state.userEmail = email;
    },
    fetchCheckTasks (state, checkTasks) {
      state.checkTasks = checkTasks;
    },
    updateCheckTasks (state, payload) {
      state.checkTasks.splice(payload.index, 1, payload.checkTask);
    },
    editCheckTask (state, payload) {
      state.checkTasks[payload.index].interval = payload.interval;
    },
    removeCheckTask (state, index) {
      state.checkTasks.splice(index, 1);
    },
    changeMainTableBusyStatus (state, status) {
      state.mainTableBusy = status;
    },
  },
  actions: {
    changeAuthStatusAction (context, authStatus) {
      console.log('changeAuthStatus action');
      context.commit('changeAuthStatus', authStatus);
    },
    setUserEmailAction (context, email) {
      console.log('setUserEmail action');
      context.commit('setUserEmail', email)
    },
    fetchCheckTasksAction (context, syncButton) {
      if (this.state.checkTasks.length === 0) {
        context.commit('changeMainTableBusyStatus', true);
      }
      console.log('fetchCheckTasks action');
      axios.get(`check-tasks/`, {
        headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` },
      }).then(response => {
        context.commit('fetchCheckTasks', response.data);
        context.commit('changeMainTableBusyStatus', false);
        if (syncButton) {
          EventBus.$emit('apiResponse', 'syncedTasks')
        }
      }).catch(e => {
        context.commit('changeMainTableBusyStatus', false);
        if (e.response) {
          EventBus.$emit('apiResponse', 'fetchTasksFail', e.response.status);
        } else {
          EventBus.$emit('apiResponse', 'fetchTasksFail', e.message);
        }
      });
    },
    appendCheckTaskAction (context, data) {
      console.log('appendCheckTask action');
      this.state.checkTasks.push(data);
      const index = this.state.checkTasks.indexOf(data);
      axios.post('check-tasks/', data, {
        headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` },
      }).then(response => {
        context.commit('updateCheckTasks', {checkTask: response.data, index: index});
        EventBus.$emit('apiResponse', 'createTaskSuccess', response.status);
      }).catch(e => {
        this.state.checkTasks.splice(index, 1)
        if (e.response) {
          EventBus.$emit('apiResponse', 'createTaskFail', e.response.status);
        } else {
          EventBus.$emit('apiResponse', 'createTaskFail', e.message);
        }
      });
    },
    editCheckTaskAction (context, payload) {
      console.log('editCheckTask action');
      const oldInterval = payload.checkTask.interval;
      if (payload.interval !== this.state.checkTasks[payload.index].interval) {
        context.commit('editCheckTask', payload);
        const dataToEdit = {interval: payload.interval}
        axios.put(`check-tasks/${payload.checkTask.id}/`, dataToEdit, {
          headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` },
        }).then(response => {
          EventBus.$emit('apiResponse', 'editTaskSuccess', response.status);
        }).catch(e => {
          this.state.checkTasks[payload.index].interval = oldInterval;
          if (e.response) {
            EventBus.$emit('apiResponse', 'editTaskFail', e.response.status);
          } else {
            EventBus.$emit('apiResponse', 'editTaskFail', e.message);
          }
        });
      }
    },
    deleteCheckTaskAction (context, payload) {
      console.log('deleteCheckTask action');
      context.commit('removeCheckTask', payload.index);
      axios.delete(`check-tasks/${payload.checkTask.id}/`, {
        headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` },
      }).then(response => {
        EventBus.$emit('apiResponse', 'deleteTaskSuccess', response.status);
      }).catch(e => {
        this.state.checkTasks.push(payload.checkTask);
        if (e.response) {
          EventBus.$emit('apiResponse', 'deleteTaskFail', e.response.status);
        } else {
          EventBus.$emit('apiResponse', 'deleteTaskFail', e.message);
        }
      });
    },
  },
});
