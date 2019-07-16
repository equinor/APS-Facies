<template>
  <static-plot
    :data-definition="dataDefinition"
    :expand="expand"
    :width="size.width"
    :height="size.height"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { Color } from '@/utils/domain/facies/helpers/colors'

import { DEFAULT_SIZE, DEFAULT_COLOR_SCALE } from '@/config'

@Component({
  components: {
    StaticPlot,
  },
})
export default class GaussianPlot extends Vue {
  @Prop({ required: true })
  readonly data!: number[][]

  @Prop({ default: false, type: Boolean })
  readonly showScale!: boolean

  @Prop({ default: DEFAULT_COLOR_SCALE })
  readonly colorScale!: string | { value: number, color: Color}[]

  @Prop({ default: false, type: Boolean })
  readonly expand!: boolean

  @Prop({ default: () => DEFAULT_SIZE })
  readonly size!: { width: number, height: number }

  get dataDefinition () {
    return [{
      z: this.data,
      zsmooth: 'best',
      type: 'heatmap',
      hoverinfo: 'none',
      colorscale: this.colorMapping,
      showscale: this.showScale,
    }]
  }
  get colorMapping () {
    if (Array.isArray(this.colorScale)) {
      const colors = []
      for (const item of this.colorScale) {
        // Plot.ly does not offer an easier way of ensure the values are discrete
        colors.push([(item.value - 1) / this.colorScale.length, item.color])
        colors.push([item.value / this.colorScale.length, item.color])
      }
      return colors
    } else {
      return this.colorScale
    }
  }
}
</script>
