<template>
  <static-plot
    v-tooltip.bottom="errorMessage"
    :data-definition="dataDefinition"
    :disabled="_disabled"
    :expand="expand"
    :width="size.width"
    :height="size.height"
  />
</template>

<script setup lang="ts">
import StaticPlot from '@/components/plot/StaticPlot.vue'

import { GaussianRandomField } from '@/utils/domain'

import { DEFAULT_SIZE } from '@/config'
import type { ColorScale, ColorMapping } from '@/components/plot/utils'
import { colorMapping as mapColors } from '@/components/plot/utils'
import { PlotData } from 'plotly.js'
import { computed } from 'vue'
import { useStore } from '../../../store'

type Props = {
  value: GaussianRandomField
  showScale?: boolean
  colorScale?: ColorScale
  expand?: boolean
  size?: { width: number, height: number }
  disabled?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  showScale: false,
  expand: false,
  size: () => DEFAULT_SIZE,
  disabled: false,
  colorScale: undefined,
})
const store = useStore()

const _colorScale = computed<ColorScale>(
  () => props.colorScale ?? store.state.options.colorScale.value,
)
const colorMapping = computed<ColorMapping>(() => mapColors(_colorScale.value))
const dataDefinition = computed<Partial<PlotData>[]>(() => [
  {
    z: props.value.simulation || undefined,
    zsmooth: 'best',
    type: 'heatmap',
    hoverinfo: 'none',
    colorscale: colorMapping.value,
    showscale: props.showScale,
  },
])

const _disabled = computed(
  () => props.disabled || !props.value.isRepresentative,
)
const errorMessage = computed(() =>
  _disabled ? 'The field has changed since it was simulated' : undefined,
)
</script>
