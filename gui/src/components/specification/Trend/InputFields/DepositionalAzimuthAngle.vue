<template>
  <storable-numeric-field
    :value="value"
    label="Azimuth (depositional)"
    property-type="angle"
    sub-property-type="azimuth"
    value-type="depositionalAzimuth"
    unit="°"
    trend
    use-modulus
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
