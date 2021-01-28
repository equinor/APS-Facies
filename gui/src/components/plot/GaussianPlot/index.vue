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
import { colorMapping, ColorScale, ColorMapping } from '../utils'
import { PlotData } from 'plotly.js'

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

  get dataDefinition (): Partial<PlotData>[] {
    return [{
      z: this.value.simulation || undefined,
      zsmooth: 'best',
      type: 'heatmap',
      hoverinfo: 'none',
      colorscale: this.colorMapping,
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore -> Type annotations are incorrect
      showscale: this.showScale,
    }]
  }

  get errorMessage (): string | undefined {
    return this._disabled
      ? 'The field has changed since it was simulated'
      : undefined
  }

  get _colorScale (): ColorScale {
    return this.colorScale || this.$store.state.options.colorScale.value
  }

  get colorMapping (): ColorMapping {
    return colorMapping(this._colorScale)
  }

  get _disabled (): boolean { return this.disabled || !this.value.isRepresentative }
}
</script>
