import Vue from 'vue'
import Router from 'vue-router'

import MainPage from 'Pages/MainPage'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Main',
      component: MainPage
    },
  ]
})
