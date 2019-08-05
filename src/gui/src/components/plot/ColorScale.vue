<template>
  <static-plot
    :data-definition="dataDefinition"
    :max-width="1"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { MinMax } from '@/api/types'
import { DEFAULT_COLOR_SCALE } from '@/config'
import StaticPlot from './StaticPlot.vue'
import { colorMapping, ColorScale } from './utils'

@Component({
  components: {
    StaticPlot,
  },
})
export default class ColorScaleLegend extends Vue {
  @Prop({ default: DEFAULT_COLOR_SCALE })
  readonly colorScale!: ColorScale

  @Prop({ default: () => { return { min: 0, max: 1 } } })
  readonly range!: MinMax

  get dataDefinition () {
    return [{
      type: 'scatter',
      x: [[0.0, 0.0], [0.1, 0.0]],
      y: [[0.0, 0.1], [0.1, 0.1]],
      mode: 'markers',
      marker: {
        size: 0.1,
        color: [this.range.min, this.range.max],
        colorscale: this.colorMapping,
        showscale: true,
        colorbar: {
          x: -2,
          xanchor: 'center',
          xpad: 0,
          ypad: 5,
          outlinewidth: 0,
          boderwidth: 0,
        },
      },
      hoverinfo: 'none'
    }]
  }

  get colorMapping () { return colorMapping(this.colorScale) }
}
</script>
