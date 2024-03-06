<template>
  <v-row
    v-if="waiting"
    justify="center"
    align="center"
  >
    <v-col
      cols="12"
      align-self="center"
    >
      <v-row justify="center">
        <v-icon
          size="x-large"
          :icon="$vuetify.icons.aliases?.refreshSpinner"
        />
      </v-row>
      <v-row justify="center">
        <span>Computing simulation box size</span>
      </v-row>
    </v-col>
  </v-row>
  <static-plot
    v-else
    v-tooltip.bottom="_disabled ? 'The field has changed since it was simulated' : undefined"
    :data-definition="dataDefinition"
    :disabled="_disabled"
    :expand="expand"
    :width="size.width"
    :height="size.height"
  />
</template>

<script setup lang="ts">
import StaticPlot from '@/components/plot/StaticPlot.vue'

import type { GaussianRandomField } from '@/utils/domain'

import { DEFAULT_SIZE } from '@/config'
import type { ColorScale, ColorMapping } from '@/components/plot/utils'
import { colorMapping as mapColors } from '@/components/plot/utils'
import type { PlotData } from 'plotly.js-dist-min'
import { computed, watch } from 'vue'
import { useOptionStore } from '@/stores/options'
import { useParameterGridSimulationBoxStore } from '@/stores/parameters/grid/simulation-box'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'

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
const optionStore = useOptionStore()
const parameterSimboxStore = useParameterGridSimulationBoxStore()

const waiting = computed<boolean>(() => {
  return parameterSimboxStore.waiting
})

const _colorScale = computed<ColorScale>(
  () => props.colorScale ?? optionStore.options.colorScale,
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

watch(waiting, async () => {
  if (!waiting.value) {
    if (!props.value.simulated) {
      await useGaussianRandomFieldStore()
        .updateSimulation(props.value)
    }
  }
})
</script>
