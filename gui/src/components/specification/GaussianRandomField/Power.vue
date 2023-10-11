<template>
  <storable-numeric-field
    :value="value"
    property-type="power"
    :arrow-step="0.01"
    value-type="power"
    label="Power"
    unit=""
    @update:error="(e: boolean) => emit('update:error', e)"
  />
</template>

<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

defineProps<{ value: GaussianRandomField }>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()
</script>
