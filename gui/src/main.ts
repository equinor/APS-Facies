// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'vue-swatches/dist/vue-swatches.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useTooltip } from './plugins/tooltip'
import { attachRMSListeners } from './plugins/rms'
import { markMissingFlexGap } from './plugins/flex-gap'
import vuetify from './plugins/vuetify'
import App from './App.vue'

const app = createApp(App)

app.use(vuetify)
app.use(createPinia())
attachRMSListeners()

useTooltip(app)
markMissingFlexGap()

app.mount('#app')
