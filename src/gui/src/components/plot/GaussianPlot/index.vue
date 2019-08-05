<template>
  <static-plot
    v-tooltip.bottom="errorMessage"
    :data-definition="dataDefinition"
    :expand="expand"
    :width="size.width"
    :height="size.height"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { GaussianRandomField } from '@/utils/domain'

import { DEFAULT_SIZE, DEFAULT_COLOR_SCALE } from '@/config'
import { colorMapping, ColorScale } from '../utils'

@Component({
  components: {
    StaticPlot,
  },
})
export default class GaussianPlot extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  @Prop({ default: false, type: Boolean })
  readonly showScale!: boolean

  @Prop({ default: DEFAULT_COLOR_SCALE })
  readonly colorScale!: ColorScale

  @Prop({ default: false, type: Boolean })
  readonly expand!: boolean

  @Prop({ default: () => DEFAULT_SIZE })
  readonly size!: { width: number, height: number }

  @Prop({ default: false, type: Boolean })
  readonly disabled: boolean

  get dataDefinition () {
    return [{
      z: this.value.simulation,
      zsmooth: 'best',
      type: 'heatmap',
      hoverinfo: 'none',
      colorscale: this.colorMapping,
      showscale: this.showScale,
      opacity: this._disabled ? 0.258823529 : 1,
    }]
  }

  get errorMessage () {
    return this._disabled
      ? 'The field has changed since it was simulated'
      : undefined
  }

  get colorMapping () {
    return colorMapping(this.colorScale)
  }

  get _disabled (): boolean { return this.disabled || !this.value.isRepresentative }
}
</script>
