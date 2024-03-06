<template>
  <numeric-field
    v-model="relativeSize"
    label="Relative size of ellipse"
    unit="%"
    fmu-updatable
    enforce-ranges
    :ranges="{ min: 0, max: 100 }"
    @update:error="(e: boolean) => emit('update:error', e)"
  />
</template>

<script setup lang="ts">
import type { GaussianRandomField } from '@/utils/domain'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

import NumericField from '@/components/selection/NumericField.vue'
import { computed } from 'vue'

const props = defineProps<{ value: GaussianRandomField }>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const relativeSize = computed({
  get: () => {
    const { value, updatable } = props.value.trend.relativeSize
    return new FmuUpdatableValue({
      value: value * 100,
      updatable,
    })
  },
  set: ({ value, updatable }: FmuUpdatableValue) =>
    (props.value.trend.relativeSize = new FmuUpdatableValue({
      value: value / 100,
      updatable: updatable,
    })),
})
</script>
