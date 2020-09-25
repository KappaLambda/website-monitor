'use strict'
const merge = require('webpack-merge')
const prodEnv = require('./prod.env')

let devSettings = {
  NODE_ENV: '"development"',
  REDIRECT_URI: `"http://localhost:8080"`,
  BASE_URL: `"http://localhost:8000/api/"`,
}

module.exports = merge(prodEnv, devSettings)
