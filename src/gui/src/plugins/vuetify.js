import Vue from 'vue'
import Vuetify from 'vuetify'

import 'vuetify/dist/vuetify.min.css'

import 'material-design-icons-iconfont/dist/material-design-icons.css'
import '@mdi/font/css/materialdesignicons.min.css'

Vue.use(Vuetify, {
  iconfont: 'mdi', // 'md' || 'mdi' || 'fa' || 'fa4'
  icons: {
    'copy': 'mdi-content-copy',
  },
})
