declare module 'vue-swatches' {
  import { Identified } from '@/utils/domain/bases/interfaces'
  import ColorLibrary from '@/utils/domain/colorLibrary'
  import type { defineComponent } from 'vue'

  type VueSwatchesProps = {
    readonly value: string
    readonly swatches: (string | { readonly colors: string[] })[]
    readonly inline: boolean
    readonly swatchesSize: number
  }
  type VueSwatchesEmits = {
    input: (value: string) => void
  }

  export default defineComponent<VueSwatchesProps, VueSwatchesEmits>()
}
