<template>
  <settings-panel title="Gaussian field transformation settings">
    <v-select
      v-model="_transformType"
      v-tooltip="
        'Choose which transformation to use for GRF. <br> The empiric transformation will always be used when the GRF has a trend. <br> The Cumulative normal is recommended for GRF without trend when running ERT using localization.'
      "
      label="Transformation type"
      :items="transformTypes"
    />
  </settings-panel>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SettingsPanel from './SettingsPanel.vue'
import type { ListItem } from '@/utils/typing'

const transformTypes: ListItem<number>[] = [
  { value: 0, title: 'Empiric Distribution function from realization of GRF' },
  { value: 1, title: 'Cumulative Normal Distribution function' },
]

const props = defineProps<{ transformType: number }>()
const emit = defineEmits<{
  (event: 'update:transformType', value: number): void
}>()

const _transformType = computed({
  get: () => props.transformType,
  set: (value: number) => emit('update:transformType', value),
})
</script>
