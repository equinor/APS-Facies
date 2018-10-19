<template>
  <static-plot
    :data-definition="dataDefinition"
  />
</template>

<script>
import VueTypes from 'vue-types'
import StaticPlot from '@/components/plot/StaticPlot'

export default {
  components: {
    StaticPlot,
  },

  props: {
    data: VueTypes.arrayOf(VueTypes.arrayOf(VueTypes.number)).isRequired,
    colorScale: VueTypes.string.def('Viridis'),
  },

  computed: {
    dataDefinition () {
      return [{
        z: this.data,
        zsmooth: 'best',
        type: 'heatmap',
        hoverinfo: 'none',
        colorscale: this.colorScale,
        showscale: false,
      }]
    },
  },
}
</script>
