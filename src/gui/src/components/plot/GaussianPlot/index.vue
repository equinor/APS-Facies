<template>
  <static-plot
    v-tooltip.bottom="errorMessage"
    :data-definition="dataDefinition"
    :disabled="_disabled"
    :expand="expand"
    :width="size.width"
    :height="size.height"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { GaussianRandomField } from '@/utils/domain'

import { DEFAULT_SIZE } from '@/config'
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

  @Prop({ default: undefined })
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
    }]
  }

  get errorMessage () {
    return this._disabled
      ? 'The field has changed since it was simulated'
      : undefined
  }

  get _colorScale () {
    return this.colorScale || this.$store.state.options.colorScale.value
  }

  get colorMapping () {
    return colorMapping(this._colorScale)
  }

  get _disabled (): boolean { return this.disabled || !this.value.isRepresentative }
}
</script>
