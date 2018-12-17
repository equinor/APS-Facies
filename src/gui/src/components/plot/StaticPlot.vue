<template>
  <vue-plot
    :data="data"
    :layout="layout"
    :options="options"
    auto-resize
  />
</template>

<script>
import VueTypes from 'vue-types'
import VuePlot from '@statnett/vue-plotly'

import { notEmpty } from '@/utils'

export default {
  components: {
    VuePlot,
  },

  props: {
    dataDefinition: VueTypes.arrayOf(Object).isRequired,
    width: VueTypes.integer.def(100),
    height: VueTypes.integer.def(100),
    staticSize: VueTypes.bool.def(false),
    svg: VueTypes.bool.def(false),
    expand: VueTypes.bool.def(false),
    axisNames: VueTypes.shape({
      x: VueTypes.oneOfType([VueTypes.string, null]).def(null),
      y: VueTypes.oneOfType([VueTypes.string, null]).def(null),
    }).def(() => { return { x: null, y: null } })
  },

  computed: {
    data () {
      if (!this.svg) {
        return this.dataDefinition
      } else {
        return [{
          type: 'scatter',
          x: [],
          y: [],
        }]
      }
    },
    layout () {
      const scaleRatio = notEmpty(this.data) && this.data.length > 0
        ? this.data.length / this.data[0].length
        : 1

      const _axis = {
        ticks: '',
        visible: false,
        zeroline: false,
        showgrid: false,
        showline: false,
        scaleratio: scaleRatio,
        autorange: true,
      }
      const xaxis = this.axisNames.x ? { ..._axis, visible: true, title: this.axisNames.x } : _axis
      const yaxis = { ..._axis, scaleanchor: 'x' }
      if (this.axisNames.y) {
        yaxis.title = this.axisNames.y
        yaxis.visible = true
      }

      const layout = {
        ...this.size(),
        showLegend: false,
        autosize: true,
        margin: {
          l: 0, r: 0, t: 0, b: 0,
        },
        xaxis,
        yaxis,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
      }
      if (this.svg) {
        layout.shapes = this.dataDefinition
      }
      return layout
    },
    options () {
      return {
        staticPlot: true,
        responsive: true,
      }
    },
  },

  methods: {
    size () {
      const parent = this.$el
        ? this.$el.parentElement
        : {
          clientWidth: this.width,
          clientHeight: this.height,
        }
      const size = this.staticSize
        ? { width: this.width, height: this.height }
        : { width: parent.clientWidth || this.width, height: parent.clientHeight || this.height }
      const val = Math.min(...Object.values(size))
      size.width = this.expand ? val : this.width
      size.height = this.expand ? val : this.height
      return size
    }
  },
}
</script>
