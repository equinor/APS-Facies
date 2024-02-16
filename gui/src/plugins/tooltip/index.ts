import { vTooltip, Tooltip, options } from 'floating-vue'
import type { App } from 'vue'

import 'floating-vue/dist/style.css'
import './style.scss'

export function useTooltip(app: App) {
  options.themes.tooltip.html = true
  app.directive('tooltip', vTooltip)
  app.component('FloatingTooltip', Tooltip)
}
