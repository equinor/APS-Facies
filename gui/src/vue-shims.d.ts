import type { Tooltip } from 'floating-vue'
import 'vite/client'

declare module '*.json' {
  const value: any
  export default value
}

declare module '@vue/runtime-core' {
  interface GlobalComponents {
    FloatingTooltip: typeof Tooltip
  }
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
