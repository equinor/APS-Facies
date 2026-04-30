<template>
  <Heatmap
    :data="chartData"
    :options="chartOptions"
    :width="props.size.width"
    :height="props.size.height"
  />
</template>

<script setup lang="ts">
import { Chart as ChartJS, LinearScale, type ChartData, type ChartOptions } from 'chart.js'
import { createTypedChart } from 'vue-chartjs'
import { computed } from 'vue'

import type { ColorScale } from '../utils'
import {
  HeatmapCellElement,
  HeatmapController,
} from '@/components/plot/Heatmap/controller.ts'
import { DEFAULT_SIZE } from '@/config.ts'

// Register the heatmap controller/element (and the linear scales it
// depends on) once with Chart.js, then create a typed Vue component
// bound to the 'heatmap' type.  vue-chartjs handles canvas creation,
// reactivity (data/options diffing) and lifecycle for us.
ChartJS.register(LinearScale)
const Heatmap = createTypedChart('heatmap', [HeatmapController, HeatmapCellElement])

type Props = {
  data: number[][]
  colorScale?: ColorScale | undefined
  size?: { width: number; height: number }
}

const props = withDefaults(defineProps<Props>(), {
  colorScale: undefined,
  size: () => ({ width: DEFAULT_SIZE.width, height: DEFAULT_SIZE.height }),
})

const chartData = computed<ChartData<'heatmap'>>(() => ({
  datasets: [
    {
      data: props.data,
      colorScale: props.colorScale,
    },
  ],
}))

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
