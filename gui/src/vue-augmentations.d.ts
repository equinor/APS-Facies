import type { Tooltip } from 'floating-vue'
import 'vite/client'

// These imports used to be part of vue-shims.d.ts, but
// vite-plus' lint / oxlint panics a bit;
// it becomes unable to import `.vue` files from `.ts` files.

declare module '@vue/runtime-core' {
  interface GlobalComponents {
    FloatingTooltip: typeof Tooltip
  }
}
