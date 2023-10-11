// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import './plugins' // TODO: What is this for? Seems old-school.

import { createApp } from 'vue'
import App from './App.vue'
const app = createApp(App)

import vuetify from './plugins/vuetify'
app.use(vuetify)

import { key, store } from './store'
app.use(store, key)

import { vTooltip, Tooltip } from 'floating-vue'
import 'floating-vue/dist/style.css'
app.directive('tooltip', vTooltip)
app.component('FloatingTooltip', Tooltip)

app.mount('#app')
