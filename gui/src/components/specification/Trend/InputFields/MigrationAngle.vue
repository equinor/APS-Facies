<template>
  <storable-numeric-field
    :value="value"
    label="Migration angle"
    property-type="angle"
    sub-property-type="migration"
    value-type="migration"
    unit="°"
    trend
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
