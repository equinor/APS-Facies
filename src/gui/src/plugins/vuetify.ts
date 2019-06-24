import '@babel/polyfill'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import 'vuetify/src/stylus/app.styl'
import 'vuetify/dist/vuetify.min.css'

import colors from 'vuetify/es5/util/colors'

// Icons
import '@fortawesome/fontawesome-free/css/all.css'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
// @ts-ignore
import Ripple from 'vuetify/es5/directives/ripple'
import { notEmpty } from '@/utils'

type Icon = string
interface Icons {
  [name: string]: Icon
}

function makeCustomIcons (): Icons {
  const icons = {
    add: 'fas fa-plus-square',
    copy: 'far fa-clone',
    paste: 'fas fa-paste',
    clipboard: 'far fa-clipboard',
    clipboardFailed: 'fas fa-exclamation-triangle',
    clipboardSuccess: 'fas fa-clipboard-check',
    import: 'fas fa-file-import fa-flip-horizontal',
    export: 'fas fa-file-export',
    remove: 'far fa-trash-alt',
    refresh: 'fas fa-sync-alt',
    random: 'fas fa-dice',
    settings: 'fas fa-cogs',
    down: 'fas fa-angle-down',
    up: 'fas fa-angle-up',
    search: 'fas fa-search',
    help: 'fas fa-question-circle',
  }
  Object.keys(icons).forEach((key: string): void => {
    if (notEmpty(icons[`${key}`])) {
      icons[`${key}Spinner`] = icons[`${key}`] + ' fa-spin'
    }
  })
  return icons
}

function makeVuetifyIcons (): Icons {
  const icons: Icons = {
    'complete': '',
    'cancel': '',
    'close': '',
    'delete': '', // delete (e.g. v-chip close)
    'clear': 'fas fa-times fa-sm',
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
    'dropdown': 'fas fa-caret-down fa-sm',
    'radioOn': '',
    'radioOff': '',
    'edit': '',
  }
  Object.keys(icons).forEach((key: Icon): void => {
    if (icons[`${key}`] === '') delete icons[`${key}`]
  })
  return icons
}
export const icons: Icons = {
  ...makeVuetifyIcons(),
  ...makeCustomIcons(),
}

Vue.use(Vuetify, {
  iconfont: 'fa', // 'md' || 'mdi' || 'fa' || 'fa4'
  icons,
  customProperties: true,
  directives: {
    Ripple
  },
  theme: {
    primary: colors.blue.darken2, // '#1976D2',
    secondary: colors.grey.darken3, // '#424242',
    accent: colors.blue.accent1, // '#82B1FF',
    error: colors.red.accent2, // '#FF5252',
    info: colors.blue.base, // '#2196F3',
    success: colors.green.base, // '#4CAF50',
    warning: colors.amber.base, // '#FFC107'
  },
})
