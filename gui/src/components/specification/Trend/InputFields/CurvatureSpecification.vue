<template>
  <storable-numeric-field
    :value="value"
    property-type="curvature"
    value-type="curvature"
    label="Curvature"
    strictly-greater
    :ranges="{ min: minCurvature, max: Number.POSITIVE_INFINITY }"
    trend
    @update:error="(e: boolean) => emit('update:error', e)"
  />
</template>

<script setup lang="ts">
import type { GaussianRandomField } from '@/utils/domain'
import StorableNumericField from '@/components/specification/StorableNumericField.vue'
import { computed } from 'vue'

const props = defineProps<{ value: GaussianRandomField }>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const minCurvature = computed(() =>
  props.value?.trend.type === 'HYPERBOLIC' ? 1 : 0,
)
</script>
