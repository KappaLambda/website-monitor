<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-custom mb-4">
    <div class="container">
      <router-link class="navbar-brand" to="/">Website Monitor</router-link>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#myNavbarCollapse" aria-controls="myNavbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="myNavbarCollapse">
        <ul class="navbar-nav mr-auto" v-if="userAuthStatus">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Checks</router-link>
          </li>
        </ul>
        <ul class="navbar-nav ml-auto">
          <li class="nav-item dropdown" v-if="userAuthStatus">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <font-awesome-icon icon="user-circle" />
            </a>
            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
              <h6 class="dropdown-header">Signed in as</h6>
              <h6 class="dropdown-header font-weight-bold text-dark">{{ userEmail }}</h6>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item" @click="logout()">Logout</button>
            </div>
          </li>
          <li class="nav-item" v-if="!userAuthStatus">
            <button
              class="btn btn-primary btn-margin"
              @click="login()">
              Log in
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import AuthService from '../../../auth/AuthService';

const auth = new AuthService();

export default {
  data () {
    this.handleAuthentication();
    this.authenticated = false;

    auth.authNotifier.on('authChange', authState => {
      this.authenticated = authState.authenticated;
    });

    auth.authNotifier.on('userEmailSet', payload => {
      this.setUserEmailAction(payload.email);
    });

    return {
      authenticated: false,
    }
  },
  computed: {
    ...mapGetters([
      'userAuthStatus',
      'userEmail',
    ]),
  },
  methods: {
    ...mapActions([
      'changeAuthStatusAction',
      'setUserEmailAction',
    ]),
    login () {
      auth.login()
    },
    handleAuthentication () {
      auth.handleAuthentication()
    },
    logout () {
      auth.logout()
    },
  },
  mounted () {
    let now = new Date().getTime();
    if (localStorage.getItem('access_token') && localStorage.getItem('expires_at') >= now) {
      this.changeAuthStatusAction(true);
    } else {
      this.changeAuthStatusAction(false);
    }
    this.setUserEmailAction(localStorage.getItem('user'));
  },
}
</script>

<style scoped>
.bg-custom {
  background-color: #3c444c!important;
}
</style>
