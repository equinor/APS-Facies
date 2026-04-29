<template>
  <Scatter :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import { DEFAULT_POINT_SIZE } from '@/config'
import type { GaussianRandomField } from '@/utils/domain'
import { Scatter } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
import { computed } from 'vue'

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

const props = defineProps<{
  value: [GaussianRandomField, GaussianRandomField]
}>()

const field = computed(() => props.value[0])
const other = computed(() => props.value[1])

const chartData = computed<ChartData<'scatter'>>(() => {
  if (!field.value.simulated || !other.value.simulated) {
    return { datasets: [] }
  }
  const xs = field.value.simulation?.flat() as number[] | undefined
  const ys = other.value.simulation?.flat() as number[] | undefined
  if (!xs || !ys) return { datasets: [] }
  const n = Math.min(xs.length, ys.length)
  const points = new Array(n)
  for (let i = 0; i < n; i++) points[i] = { x: xs[i], y: ys[i] }
  return {
    datasets: [
      {
        data: points,
        pointRadius: DEFAULT_POINT_SIZE,
        pointHoverRadius: DEFAULT_POINT_SIZE,
        backgroundColor: '#1f77b4',
      },
    ],
  }
})

const chartOptions = computed<ChartOptions<'scatter'>>(() => ({
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1,
  animation: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false },
  },
  scales: {
    x: {
      type: 'linear',
      title: { display: true, text: field.value.name },
    },
    y: {
      type: 'linear',
      title: { display: true, text: other.value.name },
    },
  },
}))
</script>
