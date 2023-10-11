<template>
  <storable-numeric-field
    :value="value"
    property-type="angle"
    sub-property-type="stacking"
    value-type="stacking"
    label="Stacking angle"
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
