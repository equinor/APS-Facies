<template>
  <settings-panel title="Logging settings">
    <v-select
      v-model="_debugLevel"
      v-tooltip="
        'The level of output to the log window can be specified.<br>For FMU setup use at least log level ON to check that model parameters are correctly updated.'
      "
      label="Debug level"
      :items="debugLevels"
      variant="underlined"
    />
  </settings-panel>
</template>

<script setup lang="ts">
import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import { computed } from 'vue'
import type { ListItem } from '@/utils/typing'

const debugLevels: ListItem<number>[] = [
  { value: 0, title: 'Off' },
  { value: 1, title: 'On' },
  { value: 2, title: 'Verbose' },
  { value: 3, title: 'Very verbose' },
  { value: 4, title: 'For debugging only' },
]

const props = defineProps<{ debugLevel: 0 | 1 | 2 | 3 | 4 }>()
const emit = defineEmits<{
  (event: 'update:debugLevel', value: number): void
}>()

const _debugLevel = computed({
  get: () => props.debugLevel,
  set: (value: number) => emit('update:debugLevel', value),
})
</script>
