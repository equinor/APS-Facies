import '@babel/polyfill'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import 'vuetify/src/stylus/app.styl'
import 'vuetify/dist/vuetify.min.css'

// Icons
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import '@mdi/font/css/materialdesignicons.min.css'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import Ripple from 'vuetify/es5/directives/ripple'

Vue.use(Vuetify, {
  iconfont: 'mdi', // 'md' || 'mdi' || 'fa' || 'fa4'
  icons: {
    'copy': 'mdi-content-copy',
  },
  customProperties: true,
  directives: {
    Ripple
  }
})
