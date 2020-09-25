import auth0 from 'auth0-js';
import EventEmitter from 'eventemitter3';
import router from '../router/router';

export default class AuthService {
  authenticated = this.isAuthenticated()
  authNotifier = new EventEmitter()

  constructor () {
    this.login = this.login.bind(this);
    this.setSession = this.setSession.bind(this);
    this.logout = this.logout.bind(this);
    this.isAuthenticated = this.isAuthenticated.bind(this);
    this.handleAuthentication = this.handleAuthentication.bind(this);
  }

  auth0 = new auth0.WebAuth({
    domain: 'website-monitor.auth0.com',
    clientID: 'gyT7SQ7O5XUyq4trptvZndrbi0gnxTrc',
    redirectUri: process.env.REDIRECT_URI,
    audience: 'https://website-monitor/api',
    responseType: 'token',
    scope: 'openid profile read:check-tasks write:check-tasks',
  });

  // this method calls the authorize() method
  // which triggers the Auth0 login page
  login () {
    console.log('login');
    this.auth0.authorize();
  }

  // this method calls the parseHash() method of Auth0
  // to get authentication information from the callback URL
  handleAuthentication () {
    console.log('handleAuthentication!!!');
    this.auth0.parseHash((err, authResult) => {
      if (authResult && authResult.accessToken) {
        this.setSession(authResult);
      } else if (err) {
        console.log(err);
        alert(`Error: ${err.error}. Check the console for further details.`);
      }
      router.replace('/');
    });
  }

  // stores the user's access_token, id_token, and a time at
  // which the access_token will expire in the local storage
  setSession (authResult) {
    console.log('setSession');
    this.auth0.client.userInfo(authResult.accessToken, (err, user) => {
      if (err) {
        localStorage.setItem('user', null);
      } else {
        localStorage.setItem('user', user.name);
        this.authNotifier.emit('userEmailSet', { email: user.name });
      }
    });
    // Set the time that the access token will expire at
    let expiresAt = JSON.stringify(
      authResult.expiresIn * 1000 + new Date().getTime()
    );
    localStorage.setItem('access_token', authResult.accessToken);
    localStorage.setItem('expires_at', expiresAt);
    this.authNotifier.emit('authChange', { authenticated: true });
  }

  // remove the access and ID tokens from the
  // local storage and emits the authChange event
  logout () {
    console.log('logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('expires_at');
    localStorage.removeItem('user');
    this.authNotifier.emit('authChange', false);
    // navigate to the home route
    this.auth0.logout({returnTo: process.env.REDIRECT_URI});
  }

  // checks if the user is authenticated
  isAuthenticated () {
    console.log('isAuthenticated');
    // Check whether the current time is past the
    // access token's expiry time
    let expiresAt = localStorage.getItem('expires_at');
    return new Date().getTime() < expiresAt;
  }

  // a static method to get the access token
  static getAuthToken () {
    console.log('getAuthToken');
    return localStorage.getItem('access_token');
  }

  // a method to get the User profile
  getUserProfile (cb) {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) return this.auth0.client.userInfo(accessToken, cb);
    else return null;
  }
}
