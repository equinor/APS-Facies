<template>
  <static-plot
    :data-definition="dataDefinition"
    :expand="expand"
    :width="size.width"
    :height="size.height"
  />
</template>

<script>
import VueTypes from 'vue-types'
import StaticPlot from '@/components/plot/StaticPlot'
import { AppTypes } from '@/utils/typing'

export default {
  components: {
    StaticPlot,
  },

  props: {
    data: VueTypes.arrayOf(VueTypes.arrayOf(VueTypes.number)).isRequired,
    colorScale: VueTypes.oneOfType([
      VueTypes.string,
      VueTypes.arrayOf(VueTypes.shape({
        value: VueTypes.integer.isRequired,
        color: AppTypes.color.isRequired,
      }))
    ]).def('Viridis'),
    expand: VueTypes.bool.def(false),
    size: VueTypes.shape({
      width: VueTypes.integer.isRequired,
      height: VueTypes.integer.isRequired,
    }).def(() => { return { width: 100, height: 100 } }).loose
  },

  computed: {
    dataDefinition () {
      return [{
        z: this.data,
        zsmooth: 'best',
        type: 'heatmap',
        hoverinfo: 'none',
        colorscale: this.colorMapping,
        showscale: false,
      }]
    },
    colorMapping () {
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
  },
}
</script>
