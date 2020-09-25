<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col" v-if="userAuthStatus">
        <div class="row table-head-controls">
          <!-- Search Tasks -->
          <form class="col-auto mr-auto my-3">
            <div class="form-inline">
              <b-input-group>
                <b-form-input v-model="filter" placeholder="Search URL" />
                <b-input-group-append>
                  <b-button :disabled="!filter" @click="filter = ''">Clear</b-button>
                </b-input-group-append>
              </b-input-group>
            </div>
          </form>
          <!-- Refresh and Create Tasks -->
          <div class="col-auto my-3">
            <button v-b-tooltip.hover.top="'Sync checks!'" class="btn btn-outline-dark" @click="getCheckTasks(syncButton=true)">
              <span class="mr-1">
                <font-awesome-icon icon="sync-alt"/>
              </span>
              <span>Refresh</span>
            </button>
            <button v-b-tooltip.hover.top="'Create new check!'" class="btn btn-success" data-toggle="modal" data-target=".app-modal" @click="resetModalInputs()">
              <span class="mr-1">
                <font-awesome-icon icon="plus"/>
              </span>
              <span>Create</span>
            </button>
          </div>
        </div>
        <!-- Main table element -->
        <b-table
          show-empty
          striped
          responsive
          fixed
          hover
          head-variant="dark"
          tbodyTrClass="cursor-pointer"
          :items="filteredCheckTasks"
          :fields="tbHeadfields"
          :current-page="currentPage"
          :per-page="parseInt(perPage)"
          :busy="mainTableBusy"
          @row-clicked="rowClickedHandler"
        >
          <template slot="table-busy" >
            <div class="text-center my-2">
              <b-spinner variant="dark" type="grow" />
            </div>
          </template>

          <template slot="empty" slot-scope="scope">
            <h6 class="text-center my-2">There are no checks. Press the <span class="badge badge-success"><font-awesome-icon icon="plus"/> Create</span> button to add one.</h6>
          </template>

          <template slot="url" slot-scope="row">
            <div class="task-url-link">
              <a v-bind:href="row.value" target="_blank">{{ row.value }}</a>
            </div>
          </template>

          <template slot="interval" slot-scope="row">
            <div class="input-group input-group-sm">
              <select class="custom-select" id="interval-select" v-model="row.value" @change="editCheckTask(row.value, row.item, row.index)">
                <option v-for="(option, index) in interval_options" :key="index">{{ option }}</option>
              </select>
            </div>
          </template>

          <template slot="last_response_status" slot-scope="row">
            <div class="task-status">
              <span class="badge badge-dark">{{ row.value }}</span>
            </div>
          </template>

          <template slot="actions" slot-scope="row">
            <div class="d-flex justify-content-around">
              <font-awesome-icon class="delete-task" icon="trash-alt" size="lg" @click="deleteCheckTask(row.item, row.index)" v-b-tooltip.hover.top="'Delete check'" />
            </div>
          </template>

          <template slot="row-details" slot-scope="row">
            <b-card>
              <app-results v-bind:taskId="row.item.id"></app-results>
            </b-card>
          </template>
        </b-table>
        <!-- Pagination Controls -->
        <div class="row table-page-control">
          <form class="col-auto mr-auto my-3">
            <div class="form-inline">
              <b-input-group>
                <label class="col-form-label mx-2">Per page</label>
                <select class="form-control" v-model="perPage">
                  <option v-for="(option, index) in pageOptions" :key="index">{{ option }}</option>
                </select>
              </b-input-group>
            </div>
          </form>
          <div class="col-auto my-3">
            <b-pagination
              :total-rows="totalRows"
              :per-page="parseInt(perPage)"
              v-model="currentPage"
            />
          </div>
        </div>

        <!-- Modal for Create and Edit -->
        <app-modal>
          <template v-slot:title>
            <h5 class="modal-title" id="appModalLabel">New Check</h5>
          </template>
          <template v-slot:form>
            <form>
              <div class="form-group">
                <label for="url" class="col-form-label">URL</label>
                <input type="text" class="form-control" id="url" v-model="url" v-validate.immediate="{required: true, url: {require_protocol: true }}" name="url">
                <p role="alert" class="alert alert-warning my-2" v-if="errors.has('url')">{{ errors.first('url') }}</p>
              </div>
              <div class="form-group">
                <label for="intervalSelect">Interval</label>
                <select class="form-control" id="intervalSelect" v-model="interval">
                  <option v-for="(option, index) in interval_options" :key="index">{{ option }}</option>
                </select>
              </div>
            </form>
          </template>
          <template v-slot:footer>
            <button class="btn btn-secondary" data-dismiss="modal">Close</button>
            <button :disabled="errors.any()" class="btn btn-success" @click="createCheckTask()" data-dismiss="modal">Create</button>
          </template>
        </app-modal>
        <!-- End of Column-Row -->
      </div>
      <app-home v-else></app-home>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

import Home from '../Home/Home.vue';
import Results from '../CheckTaskResults/CheckTaskResults.vue';
import Modal from '../../Utils/Modal.vue';

export default {
  components: {
    appModal: Modal,
    appHome: Home,
    appResults: Results,
  },
  data () {
    return {
      tbHeadfields: {
        url: {
          label: 'URL',
          class: 'text-left align-middle',
        },
        interval: {
          label: 'Interval',
          class: 'text-center align-middle',
        },
        last_response_status: {
          label: 'Status',
          class: 'text-center align-middle',
        },
        actions: {
          label: '',
          class: 'text-center align-middle',
        },
      },
      currentPage: 1,
      perPage: 10,
      pageOptions: [5, 10, 20, 50, 100],
      filter: null,
      interval_options: [60, 120, 300, 600, 1200, 1800, 3600, 7200, 21600, 43200, 86400],
      url: '',
      interval: 3600,
    };
  },
  computed: {
    ...mapGetters([
      'checkTasks',
      'userAuthStatus',
      'mainTableBusy',
    ]),
    isBusy () {
      return this.checkTasks.length === 0;
    },
    filteredCheckTasks () {
      let filtered = this.checkTasks;
      if (this.filter) {
        filtered = this.checkTasks.filter((task) => {
          return task.url.includes(this.filter);
        });
      }
      return filtered;
    },
    totalRows () {
      return this.filteredCheckTasks.length;
    },
  },
  methods: {
    ...mapActions([
      'fetchCheckTasksAction',
      'appendCheckTaskAction',
      'editCheckTaskAction',
      'deleteCheckTaskAction',
    ]),
    resetModalInputs () {
      this.url = '';
      this.interval = 3600;
    },
    getCheckTasks (syncButton = false) {
      this.fetchCheckTasksAction(syncButton);
    },
    createCheckTask () {
      this.appendCheckTaskAction({url: this.url, interval: this.interval});
    },
    editCheckTask (newValue, task, index) {
      const payload = {
        interval: newValue,
        checkTask: task,
        index: index + (this.currentPage - 1) * this.perPage,
      };
      this.editCheckTaskAction(payload);
    },
    deleteCheckTask (task, index) {
      this.deleteCheckTaskAction({checkTask: task, index: index});
    },
    rowClickedHandler (item) {
      this.$set(item, '_showDetails', !item._showDetails)
    },
  },
  mounted () {
    if (this.userAuthStatus) {
      this.getCheckTasks();
    };
  },
}
</script>

<style>
table tbody tr.cursor-pointer {
  cursor: pointer;
}

.task-url-link a {
  color: black;
  text-decoration: none;
}

.task-url-link a:hover {
  color: #007bff!important;
  text-decoration: none;
}

.task-results:hover, .edit-task:hover, .save-task:hover {
  color: #007bff!important;
  cursor: pointer;
}

.delete-task {
  color: #dc3545;
}

.delete-task:hover {
  color: darkred!important;
  cursor: pointer;
}
</style>
