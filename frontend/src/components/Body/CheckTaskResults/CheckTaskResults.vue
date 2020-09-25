<template>
  <div>
    <!-- Results Table -->
    <b-table
      show-empty
      responsive
      small
      bordered
      head-variant="dark"
      :items="results"
      :fields="tbHeadFields"
      :per-page="perPage"
      :busy="isBusy"
    >

      <template slot="table-busy" >
        <div class="text-center my-2">
          <b-spinner variant="dark" type="grow" />
        </div>
      </template>

    </b-table>
    <!-- Pagination Controls -->
    <div class="table-control">
      <b-pagination
        :total-rows="totalRows"
        :per-page="perPage"
        v-model="currentPage"
        class="my-1 float-right"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

import AuthService from '../../../auth/AuthService';
import axios from '../../../axiosConf';
import EventBus from '../../../event-bus';

export default {
  props: ['taskId'],
  data () {
    return {
      tbHeadFields: {
        status: {
          label: 'Status',
          class: 'text-center',
        },
        status_code: {
          label: 'Status Code',
          class: 'text-center',
        },
        response_time: {
          label: 'Response time',
          class: 'text-center',
        },
        date_received: {
          label: 'Date Received',
          class: 'text-center',
        },
      },
      currentPage: 1,
      lastPage: 1,
      perPage: 10,
      totalRows: 0,
      results: [],
      isBusy: true,
    }
  },
  computed: {
    ...mapGetters([
      'userAuthStatus',
    ]),
  },
  methods: {
    getCheckTaskResults () {
      console.log('getCheckTaskResults');
      axios.get(`check-tasks/${this.taskId}/results/?page=${this.currentPage}`, {
        headers: { Authorization: `Bearer ${AuthService.getAuthToken()}` },
      }).then(response => {
        const results = response.data.results
        for (let index = 0; index < results.length; index++) {
          const result = results[index];
          const date = new Date(result.date_received);
          result.date_received = String(date).split(/\s[G].+/)[0];
          result.response_time = result.response_time.toFixed(2);
        }
        this.results = results;
        this.totalRows = response.data.count;
        this.isBusy = false;
      }).catch(e => {
        this.isBusy = false;
        if (e.response) {
          EventBus.$emit('apiResponse', 'fetchTasksResultsFail', e.response.status);
        } else {
          EventBus.$emit('apiResponse', 'fetchTasksResultsFail', e.message);
        }
      });
    },
  },
  mounted () {
    this.isBusy = true;
    if (this.userAuthStatus) {
      this.getCheckTaskResults();
    };
  },
  beforeUpdate () {
    if (this.currentPage !== this.lastPage) {
      this.lastPage = this.currentPage;
      this.getCheckTaskResults();
    }
  },
}
</script>

<style scoped>
.check-task-results {
  margin-top: 1em;
  margin-bottom: 1em;
  text-align: center;
}
</style>
