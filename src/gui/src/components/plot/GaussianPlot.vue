<template>
  <vue-plot
    :data="dataDefinition"
    :layout="layout"
    :options="options"
  />
</template>

<script>
import VueTypes from 'vue-types'
import VuePlot from '@statnett/vue-plotly'
import { notEmpty } from '@/utils'

const axis = {
  ticks: '',
  visible: false,
  scaleratio: 1,
  autorange: true,
}

export default {
  components: {
    VuePlot
  },

  props: {
    data: VueTypes.arrayOf(VueTypes.arrayOf(VueTypes.number)).isRequired,
    colorScale: VueTypes.string.def('Viridis'),
  },

  data () {
    return {
      layout: {
        width: 100,
        height: 100,
        showLegend: false,
        autosize: false,
        margin: {
          l: 0, r: 0, t: 0, b: 0,
        },
        xaxis: axis,
        yaxis: { ...axis, scaleanchor: 'x' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
      },
      options: {
        staticPlot: true
      }
    }
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

  beforeUpdate () {
    this.resize()
  },

  methods: {
    resize () {
      // Update Scale ratio
      const scaleRatio = notEmpty(this.data) && this.data.length > 0
        ? this.data.length / this.data[0].length
        : 1
      this.layout.xaxis.scaleratio = scaleRatio
      this.layout.yaxis.scaleratio = scaleRatio

      // Update plot size
      const parent = this.$el.parentElement
      this.layout.height = parent.clientHeight
      this.layout.width = parent.clientWidth
    },
  },
}
</script>
