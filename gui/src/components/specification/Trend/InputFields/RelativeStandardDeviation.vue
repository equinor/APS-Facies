<template>
  <storable-numeric-field
    :value="value"
    :arrow-step="0.01"
    :ranges="ranges"
    property-type="relativeStdDev"
    label="Relative std. dev."
    trend
    @update:error="(e: boolean) => emit('update:error', e)"
  />
</template>

<script setup lang="ts">
import StorableNumericField from '@/components/specification/StorableNumericField.vue'
import { GaussianRandomField } from '@/utils/domain'
import { MinMax } from '@/api/types'

defineProps<{ value: GaussianRandomField }>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()
const ranges: MinMax = { min: 0, max: 1 }
</script>
