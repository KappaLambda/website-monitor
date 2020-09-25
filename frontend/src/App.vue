<template>
  <div class="my-app">
    <app-navbar></app-navbar>
    <router-view></router-view>
    <vue-snotify></vue-snotify>
  </div>
</template>

<script>
import Navbar from './components/Header/Navbar/Navbar.vue';

import EventBus from './event-bus';

export default {
  name: 'App',
  components: {
    appNavbar: Navbar,
  },
  mounted () {
    EventBus.$on('apiResponse', (event, status) => {
      let message = 'Response code: ' + status;
      if (status === 'Network Error') {
        message = 'Error: ' + status;
      }
      switch (event) {
        case 'fetchTasksFail':
          this.$snotify.error('Failed to fetch checks.\n' + message);
          break;

        case 'createTaskSuccess':
          this.$snotify.success('Created new check.')
          break;

        case 'createTaskFail':
          this.$snotify.error('Failed to create new check.\n' + message);
          break;

        case 'editTaskSuccess':
          this.$snotify.success('Edited check.')
          break;

        case 'editTaskFail':
          this.$snotify.error('Failed to edit check.\n' + message);
          break;

        case 'deleteTaskSuccess':
          this.$snotify.success('Deleted check.')
          break;

        case 'deleteTaskFail':
          this.$snotify.error('Failed to delete check.\n' + message);
          break;

        case 'fetchTasksResultsFail':
          this.$snotify.error('Failed to fetch check results.\n' + message);
          break;

        case 'syncedTasks':
          this.$snotify.success('Fetched checks.');
          break;
      }
    });
  },
}
</script>

<style>
.my-app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
