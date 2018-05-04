// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import Vuetify from 'vuetify'
import App from './App.vue'
import router from './router'
import store from './store'

import 'vuetify/dist/vuetify.min.css'
import 'material-design-icons/iconfont/material-icons.css'

Vue.use(Vuetify)
Vue.config.productionTip = process.env.NODE_ENV !== 'production'

/* eslint-disable no-new */
/* tslint:disable no-unused-expression */
new Vue({
  el: '#app',
  components: { App },
  router,
  store,
  template: '<App/>',
})
