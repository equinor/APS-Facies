<template>
  <Heatmap
    :data="chartData"
    :options="chartOptions"
    :width="canvasSize.width"
    :height="canvasSize.height"
    :style="canvasStyle"
  />
</template>

<script setup lang="ts">
import {
  Chart as ChartJS,
  LinearScale,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
import { createTypedChart } from 'vue-chartjs'
import { computed } from 'vue'

import type { ColorScale } from '../utils'
import {
  HeatmapCellElement,
  HeatmapController,
} from '@/components/plot/Heatmap/controller.ts'
import { DEFAULT_SIZE } from '@/config.ts'
import { getDisabledOpacity } from '@/utils/helpers/simple'

// Register the heatmap controller/element (and the linear scales it
// depends on) once with Chart.js, then create a typed Vue component
// bound to the 'heatmap' type.  vue-chartjs handles canvas creation,
// reactivity (data/options diffing) and lifecycle for us.
ChartJS.register(LinearScale)
const Heatmap = createTypedChart('heatmap', [
  HeatmapController,
  HeatmapCellElement,
])

type Props = {
  data: number[][] | null
  colorScale?: ColorScale | undefined
  size?: { width: number; height: number }
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  colorScale: undefined,
  size: () => ({ width: DEFAULT_SIZE.width, height: DEFAULT_SIZE.height }),
  disabled: false,
})

const opacity = computed(() => getDisabledOpacity(props.disabled))

/**
 * The canvas is sized to match the data's aspect ratio (cols × rows),
 * scaled up uniformly so that it is at least `size.width × size.height`.
 * `props.size` thus acts as a minimum bound rather than a fixed size,
 * which prevents non-square data from being squashed into a square box.
 */
const canvasSize = computed(() => {
  const data = props.data
  const rows = data?.length ?? 0
  const cols = rows > 0 ? (data?.[0]?.length ?? 0) : 0
  if (rows <= 0 || cols <= 0) {
    return { width: props.size.width, height: props.size.height }
  }
  const scale = Math.max(1, props.size.width / cols, props.size.height / rows)
  return {
    width: Math.round(cols * scale),
    height: Math.round(rows * scale),
  }
})

const canvasStyle = computed(() => ({
  opacity: opacity.value,
  width: `${canvasSize.value.width}px`,
  height: `${canvasSize.value.height}px`,
}))

const chartData = computed<ChartData<'heatmap'>>(() =>
  props.data
    ? {
        datasets: [
          {
            data: props.data,
            colorScale: props.colorScale,
          },
        ],
      }
    : {
        datasets: [],
      },
)

const chartOptions = computed<ChartOptions<'heatmap'>>(() => ({
  // Disable Chart.js' ResizeObserver-driven auto-resize: it fights with
  // an unsized parent and produces the "accordion" effect where the
  // canvas keeps growing on every layout pass.  Width/height are passed
  // explicitly via the component's props instead.
  responsive: false,
  maintainAspectRatio: false,
  animation: false,
  transitions: {
    active: { animation: { duration: 0 } },
    resize: { animation: { duration: 0 } },
    show: { animation: { duration: 0 } },
    hide: { animation: { duration: 0 } },
  },
}))
</script>
