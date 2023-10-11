<template>
  <static-plot
    :data-definition="dataDefinition"
    :axis-names="{ x: field.name, y: other.name }"
  />
</template>

<script setup lang="ts">
import { DEFAULT_POINT_SIZE } from '@/config'
import StaticPlot from '@/components/plot/StaticPlot.vue'
import { GaussianRandomField } from '@/utils/domain'
import { PlotData } from 'plotly.js'
import { computed } from 'vue'

const props = defineProps<{
  value: [GaussianRandomField, GaussianRandomField]
}>()

const field = computed(() => props.value[0])
const other = computed(() => props.value[1])

const dataDefinition = computed<Partial<PlotData>[]>(() =>
  field.value.simulated && other.value.simulated
    ? [
        {
          type: 'scattergl',
          mode: 'markers',
          marker: { size: DEFAULT_POINT_SIZE },
          x: field.value.simulation?.flat(),
          y: other.value.simulation?.flat(),
        },
      ]
    : [],
)
</script>
