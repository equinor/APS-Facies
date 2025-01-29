<template>
  <plotly-plot
    ref="plot"
    :id="id"
    :data="__content"
    :layout="__layout"
    :options="__options"
    auto-resize
    @click="(e: MouseEvent) => $emit('click', e)"
    @resize="resize"
  />
</template>

<script setup lang="ts">
import { getDisabledOpacity } from '@/utils/helpers/simple'
import { notEmpty } from '@/utils'
import { DEFAULT_SIZE } from '@/config'
import type { Optional } from '@/utils/typing'
import type {
  Annotations,
  Config,
  Layout,
  LayoutAxis,
  PlotData,
  Shape,
} from 'plotly.js-dist-min'
import { ref, computed, onBeforeUnmount, onMounted, onBeforeMount } from 'vue'
import PlotlyPlot from './PlotlyPlot.vue'

type Size = {
  width: number
  height: number
}

type Props = {
  dataDefinition: Partial<PlotData | Shape>[]
  annotations?: Array<Partial<Annotations>>
  width?: number
  height?: number
  maxWidth?: number
  maxHeight?: number
  staticSize?: boolean
  svg?: boolean
  expand?: boolean
  disabled?: boolean
  axisNames?: Record<'x' | 'y', Optional<string>>
  id?: string
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
  id: undefined,
  axisNames: () => ({ x: null, y: null }),
})

const size = ref<Size>({ height: 0, width: 0 })
const plot = ref<InstanceType<typeof PlotlyPlot> | null>(null)

const __content = computed<Partial<PlotData>[]>(() => {
  if (!props.svg) {
    return (props.dataDefinition as Partial<PlotData>[]).map((obj) => {
      const opacity = getDisabledOpacity(props.disabled)
      return {
        ...obj,
        height: props.height,
        width: props.width,
        opacity,
      }
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

function getScaleRatio(data: Partial<PlotData>[]): number {
  if (!notEmpty(data) || data.length === 0) return 1
  const { x, y } = data[0]
  if (!x || !y) return 1
  if (x?.length === 0 || y?.length === 0) return 1
  return x.length / y.length
}

const __layout = computed<Partial<Layout>>(() => {
  const scaleRatio = getScaleRatio(__content.value)

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
  const opacity = getDisabledOpacity(props.disabled)

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
    ...(props.svg && {
      shapes: (props.dataDefinition as Partial<Shape>[]).map((shape) => {
        return {
          ...shape,
          opacity,
        } as Partial<Shape>
      }),
    }),
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
  // Do not set the size if it would become 0
  if (props.expand && val === 0) return
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
