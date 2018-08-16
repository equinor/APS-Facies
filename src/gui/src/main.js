// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './plugins/vuetify'
import './plugins/ag-grid'
import './plugins/axios'
import './plugins/validation'

Vue.config.productionTip = process.env.NODE_ENV !== 'production'

/* eslint-disable no-new */
/* tslint:disable no-unused-expression */
new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
