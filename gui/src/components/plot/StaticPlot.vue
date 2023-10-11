<template>
  <plotly-plot
    :data="__content"
    :layout="__layout"
    :options="__options"
    auto-resize
    @click="(e) => $emit('click', e)"
    @resize="resize"
    ref="plot"
  />
</template>

<script setup lang="ts">
import { getDisabledOpacity } from '@/utils/helpers/simple'

// TODO: REPLACE (had some issues with d3 not working.)
// import VuePlot from "@statnett/vue-plotly";

import { notEmpty } from '@/utils'
import { DEFAULT_SIZE } from '@/config'
import { Optional } from '@/utils/typing'
import { Config, Layout, LayoutAxis, PlotData, Shape } from 'plotly.js'
import { ref, computed, onBeforeUnmount, onMounted, onBeforeMount } from 'vue'
import PlotlyPlot from './PlotlyPlot.vue'

type Size = {
  width: number
  height: number
}

type Props = {
  dataDefinition: Partial<PlotData | Shape>[]
  annotations?: Record<string, unknown>[]
  width?: number
  height?: number
  maxWidth?: number
  maxHeight?: number
  staticSize?: boolean
  svg?: boolean
  expand?: boolean
  disabled?: boolean
  axisNames?: { x: Optional<string>; y: Optional<string> }
}
const props = withDefaults(defineProps<Props>(), {
  annotations: () => [],
  width: DEFAULT_SIZE.width,
  height: DEFAULT_SIZE.height,
  maxWidth: DEFAULT_SIZE.max.width,
  maxHeight: DEFAULT_SIZE.max.height,
  staticSize: false,
  svg: false,
  expand: false,
  disabled: false,
  axisNames: () => ({ x: null, y: null }),
})

const size = ref<Size>({ height: 0, width: 0 })
const plot = ref<InstanceType<typeof PlotlyPlot> | null>(null)

const __content = computed<Partial<PlotData>[]>(() => {
  if (!props.svg) {
    return (props.dataDefinition as Partial<PlotData>[]).map((obj) => {
      // @ts-ignore
      obj.opacity = getDisabledOpacity(this.disabled)
      return obj
    })
  } else {
    return [
      {
        type: 'scatter',
        x: [],
        y: [],
      },
    ]
  }
})

const __layout = computed<Partial<Layout>>(() => {
  const scaleRatio =
    notEmpty(__content.value) && __content.value.length > 0
      ? __content.value.length / (__content.value[0].x?.length ?? 1)
      : 1

  const _axis: Partial<LayoutAxis> = {
    ticks: '',
    visible: false,
    zeroline: false,
    showgrid: false,
    showline: false,
    scaleratio: scaleRatio,
    autorange: true,
    titlefont: {
      family: 'Roboto',
    },
  }
  const xaxis: Partial<LayoutAxis> = props.axisNames.x
    ? { ..._axis, visible: true, title: props.axisNames.x }
    : _axis
  const yaxis: Partial<LayoutAxis> = {
    ..._axis,
    scaleanchor: 'x',
    ...(props.axisNames.y && {
      title: props.axisNames.y,
      visible: true,
    }),
  }

  return {
    ...size.value,
    showlegend: false,
    autosize: true,
    margin: {
      l: 0,
      r: 0,
      t: 0,
      b: 0,
    },
    xaxis,
    yaxis,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    paper_bgcolor: 'rgba(0,0,0,0)',
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    plot_bgcolor: 'rgba(0,0,0,0)',
    ...(props.svg && { shapes: props.dataDefinition as Partial<Shape>[] }),
    annotations: props.annotations,
  }
})

const __options = computed<Partial<Config>>(() => ({
  staticPlot: true,
  responsive: true,
}))

function resize(): void {
  const parent = plot.value?.$el.getElementsByClassName(
    'svg-container',
  )?.[0] ?? {
    clientWidth: props.width,
    clientHeight: props.height,
  }
  const newSize = props.staticSize
    ? { width: props.width, height: props.height }
    : {
        width: parent.clientWidth ?? props.width,
        height: parent.clientHeight ?? props.height,
      }
  const val = Math.max(...Object.values(newSize))
  size.value.width = props.expand ? Math.min(val, props.maxWidth) : props.width
  size.value.height = props.expand
    ? Math.min(val, props.maxHeight)
    : props.height
}

onBeforeMount(() => {
  size.value.width = props.width
  size.value.height = props.height
})
onMounted(() => {
  window.addEventListener('resize', resize)
  resize()
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
})
</script>
