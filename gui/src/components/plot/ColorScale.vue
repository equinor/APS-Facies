<template>
  <static-plot :data-definition="dataDefinition" :max-width="1" />
</template>

<script setup lang="ts">
import { MinMax } from '@/api/types'
import StaticPlot from './StaticPlot.vue'
import type { ColorMapping, ColorScale } from './utils'
import { colorMapping as mapColors } from './utils'
import { PlotData } from 'plotly.js'
import { computed } from 'vue'
import { useOptionStore } from '@/stores/options'

type Props = {
  colorScale?: ColorScale
  range?: MinMax
}
const props = withDefaults(defineProps<Props>(), {
  range: () => ({ min: 0, max: 1 }),
})
const optionStore = useOptionStore()

const _colorScale = computed<ColorScale>(
  () => props.colorScale || optionStore.options.colorScale,
)
const colorMapping = computed<ColorMapping>(() => mapColors(_colorScale.value))
const dataDefinition = computed<Partial<PlotData>[]>(() => [
  {
    type: 'scatter',
    x: [
      [0.0, 0.0],
      [0.1, 0.0],
    ],
    y: [
      [0.0, 0.1],
      [0.1, 0.1],
    ],
    mode: 'markers',
    marker: {
      size: 0.1,
      color: [props.range.min, props.range.max],
      colorscale: colorMapping.value,
      showscale: true,
      colorbar: {
        x: -2,
        xanchor: 'center',
        xpad: 0,
        ypad: 5,
        outlinewidth: 0,
        borderwidth: 0,
      },
    },
    hoverinfo: 'none',
  },
])
</script>
