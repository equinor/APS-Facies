<template>
  <vue-plot
    :data="__content"
    :layout="__layout"
    :options="__options"
    auto-resize
    @click.native="e => $emit('click', e)"
    @resize="resize"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

// @ts-ignore
import VuePlot from '@statnett/vue-plotly'

import { notEmpty } from '@/utils'

import { DEFAULT_SIZE } from '@/config'

import { Optional } from '@/utils/typing'
import { PlotData } from 'plotly.js'

@Component({
  components: {
    VuePlot,
  },
})
export default class StaticPlot extends Vue {
  @Prop({ required: true })
  readonly dataDefinition!: Partial<PlotData>[]

  @Prop({ default: () => [] })
  readonly annotations!: object[]

  @Prop({ default: DEFAULT_SIZE.width })
  readonly width!: number

  @Prop({ default: DEFAULT_SIZE.height })
  readonly height!: number

  @Prop({ default: DEFAULT_SIZE.max.width })
  readonly maxWidth!: number

  @Prop({ default: DEFAULT_SIZE.max.height })
  readonly maxHeight!: number

  @Prop({ default: false, type: Boolean })
  readonly staticSize!: boolean

  @Prop({ default: false, type: Boolean })
  readonly svg!: boolean

  @Prop({ default: false, type: Boolean })
  readonly expand!: boolean

  @Prop({ default: false, type: Boolean })
  readonly disabled: boolean

  @Prop({ default: () => { return { x: null, y: null } } })
  readonly axisNames!: { x: Optional<string>, y: Optional<string> }

  size: { height: number, width: number } = {
    height: 0,
    width: 0,
  }

  get __content () {
    if (!this.svg) {
      return this.dataDefinition
        .map(obj => {
          // @ts-ignore
          obj.opacity = this.disabled ? 0.258823529 : 1
          return obj
        })
    } else {
      return [{
        type: 'scatter',
        x: [],
        y: [],
      }]
    }
  }

  get __layout () {
    const scaleRatio = notEmpty(this.__content) && this.__content.length > 0
      // @ts-ignore
      ? this.__content.length / this.__content[0].length
      : 1

    const _axis = {
      ticks: '',
      visible: false,
      zeroline: false,
      showgrid: false,
      showline: false,
      scaleratio: scaleRatio,
      autorange: true,
      titlefont: {
        family: 'Roboto'
      },
    }
    const xaxis = this.axisNames.x ? { ..._axis, visible: true, title: this.axisNames.x } : _axis
    const yaxis = {
      ..._axis,
      scaleanchor: 'x',
      ...(this.axisNames.y && {
        title: this.axisNames.y,
        visible: true,
      }),
    }

    return {
      ...this.size,
      showLegend: false,
      autosize: true,
      margin: {
        l: 0, r: 0, t: 0, b: 0,
      },
      xaxis,
      yaxis,
      /* eslint-disable-next-line @typescript-eslint/camelcase */
      paper_bgcolor: 'rgba(0,0,0,0)',
      /* eslint-disable-next-line @typescript-eslint/camelcase */
      plot_bgcolor: 'rgba(0,0,0,0)',
      ...(this.svg && { shapes: this.dataDefinition }),
      ...(this.annotations && { annotations: this.annotations }),
    }
  }
  get __options () {
    return {
      staticPlot: true,
      responsive: true,
    }
  }

  beforeDestroy () {
    window.removeEventListener('resize', this.resize)
  }

  beforeMount () {
    this.size.width = this.width
    this.size.height = this.height
  }

  mounted () {
    window.addEventListener('resize', this.resize)

    this.$watch('$el', this.resize)
  }

  resize () {
    const parent = this.$el
      ? this.$el.getElementsByClassName('svg-container')[0]
      : {
        clientWidth: this.width,
        clientHeight: this.height,
      }
    const size = this.staticSize
      ? { width: this.width, height: this.height }
      : { width: parent.clientWidth || this.width, height: parent.clientHeight || this.height }
    const val = Math.max(...Object.values(size))
    this.size.width = this.expand ? Math.min(val, this.maxWidth) : this.width
    this.size.height = this.expand ? Math.min(val, this.maxHeight) : this.height
  }
}
</script>
