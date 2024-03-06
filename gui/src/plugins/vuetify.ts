import 'vuetify/styles'
import { createVuetify, type IconAliases } from 'vuetify'
import { aliases, fa } from 'vuetify/iconsets/fa'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import '@/style/main.scss'

import colors from 'vuetify/util/colors'

// Icons
import '@fortawesome/fontawesome-free/css/all.css'
import 'roboto-fontface/css/roboto/roboto-fontface.css'

function makeCustomIcons(): Partial<IconAliases> {
  const customIcons: { [key: string]: string } = {
    add: 'fas fa-plus-square',
    changelog: 'far fa-newspaper',
    clipboard: 'far fa-clipboard',
    clipboardFailed: 'fas fa-exclamation-triangle',
    clipboardSuccess: 'fas fa-clipboard-check',
    copy: 'far fa-clone',
    down: 'fas fa-angle-down',
    export: 'fas fa-file-export',
    folder: 'far fa-folder',
    folderOpen: 'far fa-folder-open',
    fromRoxar: 'fas fa-desktop',
    help: 'fas fa-question-circle',
    import: 'fas fa-file-import fa-flip-horizontal',
    observed: 'far fa-eye',
    observedNegated: 'far fa-eye-slash',
    openFolder: 'far fa-folder-open',
    paste: 'fas fa-paste',
    random: 'fas fa-dice',
    refresh: 'fas fa-sync-alt',
    remove: 'far fa-trash-alt',
    search: 'fas fa-search',
    settings: 'fas fa-cogs',
    up: 'fas fa-angle-up',
  }
  for (const iconKey of Object.keys(customIcons)) {
    customIcons[`${iconKey}Spinner`] = customIcons[iconKey] + ' fa-spin'
    customIcons[`${iconKey}Negated`] = customIcons[`${iconKey}Negated`] ?? ''
  }
  return customIcons
}

function makeVuetifyIcons(): Partial<IconAliases> {
  const vuetifyIcons: { [key: string]: string } = {
    clear: 'fas fa-times fa-sm',
    dropdown: 'fas fa-caret-down fa-sm',
    expand: 'fas fa-chevron-down', // 'menu': '',
  }
  for (const iconKey of Object.keys(vuetifyIcons)) {
    if (vuetifyIcons[iconKey] === '') delete vuetifyIcons[iconKey]
  }
  return vuetifyIcons
}

const extendedAliases: Partial<IconAliases> = {
  ...aliases,
  ...makeVuetifyIcons(),
  ...makeCustomIcons(),
}

export default createVuetify({
  icons: {
    defaultSet: 'fa', // 'md' || 'mdi' || 'fa' || 'fa4'
    aliases: extendedAliases,

    // aliases,
    sets: { fa },
  },
  components: {
    ...components,
  },
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: colors.blue.darken2, // '#1976D2',
          secondary: colors.grey.darken3, // '#424242',
          accent: colors.blue.accent1, // '#82B1FF',
          error: colors.red.accent2, // '#FF5252',
          info: colors.blue.base, // '#2196F3',
          success: colors.green.base, // '#4CAF50',
          warning: colors.amber.base, // '#FFC107'
        },
      },
    },
  },
})
