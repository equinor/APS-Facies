<template>
    <canvas ref="canvas"/>
</template>

<script setup lang="ts">
import { Chart as ChartJS, type ChartConfiguration, LinearScale } from 'chart.js';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { ColorScale } from '../utils'
import { HeatmapCellElement, HeatmapController } from "@/components/plot/Heatmap/controller.ts";
import { DEFAULT_SIZE } from "@/config.ts";

type Props = {
  data: number[][]
  colorScale?: ColorScale | undefined
  size?: { width: number; height: number }
}

const props = withDefaults(defineProps<Props>(), {
  colorScale: undefined,
  size: () => ({width: DEFAULT_SIZE.width, height: DEFAULT_SIZE.height }),
})

const canvas = ref<HTMLCanvasElement | null>(null)
let chart: ChartJS<'heatmap'> | null = null

function buildConfig(): ChartConfiguration<'heatmap'> {
  return {
    type: 'heatmap',
    data: {
      datasets: [
        {
          data: props.data,
          colorScale: props.colorScale,
        },
      ],
    },
    options: {
      animation: false,
      transitions: {
        active: { animation: { duration: 0 } },
        resize: { animation: { duration: 0 } },
        show: { animation: { duration: 0 } },
        hide: { animation: { duration: 0 } },
      },
    },
  }
}

onMounted(() => {
  if (!canvas.value) return
  chart = new ChartJS<'heatmap'>(canvas.value, buildConfig())
})

watch(() => [props.size.width, props.size.height], () => {
  if (!chart) return
  chart.resize(props.size.width, props.size.height)
})

watch(
  () => [props.data, props.colorScale],
  () => {
    if (!chart) return
    const ds = chart.data.datasets[0]
    if (!ds) return
    ds.data = props.data
    ds.colorScale = props.colorScale
    chart.update()
  },
  { deep: false },
)

onBeforeUnmount(() => {
  chart?.destroy()
  chart = null
})

ChartJS.register(HeatmapCellElement, HeatmapController, LinearScale)

</script>

