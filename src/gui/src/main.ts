// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'
import store from './store'
import './plugins'
import vuetify from './plugins/vuetify'

import { isDevelopmentBuild } from '@/config'

Vue.config.productionTip = isDevelopmentBuild()

/* eslint-disable no-new */
new Vue({
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
