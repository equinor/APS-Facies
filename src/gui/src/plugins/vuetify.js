import '@babel/polyfill'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import 'vuetify/src/stylus/app.styl'
import 'vuetify/dist/vuetify.min.css'

// Icons
import '@fortawesome/fontawesome-free/css/all.css'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import Ripple from 'vuetify/es5/directives/ripple'
import { notEmpty } from '@/utils'

function makeCustomIcons () {
  const icons = {
    add: 'fas fa-plus-square',
    copy: 'fas fa-clone',
    remove: 'fas fa-trash',
    refresh: 'fas fa-sync-alt',
    random: 'fas fa-dice',
    settings: 'fas fa-sliders-h',
  }
  Object.keys(icons).forEach(key => {
    if (notEmpty(icons[`${key}`])) {
      icons[`${key}Spinner`] = icons[`${key}`] + ' fa-spin'
    }
  })
  return icons
}

function makeVuetifyIcons () {
  const icons = {
    'complete': '',
    'cancel': '',
    'close': '',
    'delete': '', // delete (e.g. v-chip close)
    'clear': '',
    'success': '',
    'info': '',
    'warning': '',
    'error': '',
    'prev': '',
    'next': '',
    'checkboxOn': '',
    'checkboxOff': '',
    'checkboxIndeterminate': '',
    'delimiter': '', // for carousel
    'sort': '',
    'expand': 'fas fa-angle-down', // 'menu': '',
    'subgroup': '',
    'dropdown': 'fas fa-caret-down',
    'radioOn': '',
    'radioOff': '',
    'edit': '',
  }
  Object.keys(icons).forEach(key => {
    if (icons[`${key}`] === '') delete icons[`${key}`]
  })
  return icons
}
export const icons = {
  ...makeVuetifyIcons(),
  ...makeCustomIcons(),
}

Vue.use(Vuetify, {
  iconfont: 'fa', // 'md' || 'mdi' || 'fa' || 'fa4'
  icons,
  customProperties: true,
  directives: {
    Ripple
  }
})
