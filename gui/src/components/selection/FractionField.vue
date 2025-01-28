<template>
  <numeric-field
    :model-value="modelValue"
    :arrow-step="0.01"
    :ranges="ranges"
    :fmu-updatable="fmuUpdatable"
    :disabled="disabled"
    :label="label"
    :append-icon="appendIcon"
    :dense="dense"
    optional
    enforce-ranges
    @update:model-value="(newValue) => emit('update:model-value', newValue)"
    @click:append="(e: MouseEvent) => emit('click:append', e)"
  />
</template>

<script setup lang="ts">
import type { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'

import type { MinMax } from '@/api/types'
import NumericField from '@/components/selection/NumericField.vue'
import type { PROBABILITY } from '@/utils/domain/types'

const ranges: MinMax = { min: 0, max: 1 }
type Props = {
  modelValue: number | FmuUpdatable | null
  fmuUpdatable?: boolean
  disabled?: boolean
  label?: string
  appendIcon?: string
  dense?: boolean
}
withDefaults(defineProps<Props>(), {
  fmuUpdatable: false,
  disabled: false,
  label: '',
  appendIcon: '',
  dense: false,
})
const emit = defineEmits<{
  (event: 'click:append', value: MouseEvent): void
  (
    event: 'update:model-value',
    value: PROBABILITY | FmuUpdatable<PROBABILITY> | null,
  ): void
}>()
</script>
