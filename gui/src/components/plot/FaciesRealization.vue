<template>
  <v-row class="ma-0 pa-0 shrink" align="center" justify="center">
    <static-plot
      v-tooltip.bottom="errorMessage"
      :data-definition="dataDefinition"
      :disabled="_disabled"
      :expand="expand"
    />
  </v-row>
</template>

<script setup lang="ts">
import { PlotData } from 'plotly.js'

import { GlobalFacies, TruncationRule } from '@/utils/domain'

import StaticPlot from '@/components/plot/StaticPlot.vue'
import { useStore } from '../../store'
import { computed } from 'vue'

function filterOnCode(data: number[][] | null, code: number): (1 | null)[][] {
  if (!data) return []
  return data.map((arr) => arr.map((val) => (val === code ? 1 : null)))
}

type Props = {
  value: TruncationRule
  expand?: boolean
  disabled?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  expand: false,
  disabled: false,
})
const store = useStore()

const faciesTable = computed<GlobalFacies[]>(
  () => store.getters['facies/global/selected'],
)

const _disabled = computed(
  () => props.disabled || !props.value.isRepresentative,
)

const errorMessage = computed(() =>
  _disabled.value
    ? 'The truncation rule has changed since it was simulated'
    : undefined,
)

const dataDefinition = computed<Partial<PlotData>[]>(() =>
  faciesTable.value.map(({ color, code }) => {
    return {
      z: filterOnCode(props.value.realization, code),
      zsmooth: 'best',
      type: 'heatmap',
      hoverinfo: 'none',
      colorscale: [
        [0, color],
        [1, color],
      ],
      showscale: false,
    }
  }),
)
</script>
