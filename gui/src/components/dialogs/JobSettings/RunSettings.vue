<template>
  <settings-panel title="Run settings">
    <v-row>
      <v-col cols="6">
        <numeric-field
          v-model="_maxAllowedFractionOfValuesOutsideTolerance"
          v-tooltip="
            'Max allowed fraction of grid cell values in probability cubes without proper normalization. <br> Default value is 10%'
          "
          label="Max allowed fraction of non-normalized grid cells"
          :ranges="{ min: 0, max: 100 }"
          unit="%"
        />
      </v-col>
      <v-col cols="6">
        <numeric-field
          v-model="_toleranceOfProbabilityNormalisation"
          v-tooltip="
            'If the sum of facies probabilities is outside the interval <br>[1-tolerance, 1+tolerance], an error message will be given (job will not run), <br>but if inside this interval, the probabilities will be normalized to 1.<br>Default value is 0.2.'
          "
          label="Max allowed tolerance for non-normalized probabilities"
          :ranges="{ min: 0, max: 100 }"
          unit="%"
        />
      </v-col>
    </v-row>
  </settings-panel>
</template>

<script setup lang="ts">
import NumericField from '@/components/selection/NumericField.vue'
import SettingsPanel from './SettingsPanel.vue'
import { computed } from 'vue'

type Props = {
  maxAllowedFractionOfValuesOutsideTolerance: number
  toleranceOfProbabilityNormalisation: number
}
const props = defineProps<Props>()
const emit = defineEmits<{
  (event: 'update:maxAllowedFractionOfValuesOutsideTolerance', value: number): void
  (event: 'update:toleranceOfProbabilityNormalisation', value: number): void
}>()

const _maxAllowedFractionOfValuesOutsideTolerance = computed({
  get: () => props.maxAllowedFractionOfValuesOutsideTolerance * 100,
  set: (value: number) =>
    emit('update:maxAllowedFractionOfValuesOutsideTolerance', value / 100),
})

const _toleranceOfProbabilityNormalisation = computed({
  get: () => props.toleranceOfProbabilityNormalisation * 100,
  set: (value: number) =>
    emit('update:toleranceOfProbabilityNormalisation', value / 100),
})
</script>
