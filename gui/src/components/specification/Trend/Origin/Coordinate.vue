<template>
  <storable-numeric-field
    :value="value"
    :property-type="propertyType"
    :ranges="ranges"
    :sub-property-type="coordinateAxis"
    :label="shownLabel"
    :arrow-step="arrowStep"
    allow-negative
    enforce-ranges
    trend
    @update:error="(e: boolean) => emit('update:error', e)"
  />
</template>

<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'
import StorableNumericField from '@/components/specification/StorableNumericField.vue'
import { notEmpty } from '@/utils'
import { computed } from 'vue'

type Props = {
  value: GaussianRandomField
  originType: string
  coordinateAxis: string
  label?: string
}
const props = withDefaults(defineProps<Props>(), { label: '' })
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const propertyType = 'origin'

const isRelative = computed(() => props.originType === 'RELATIVE')
const ranges = computed(() =>
  isRelative.value ? { min: 0, max: 1 } : { min: -Infinity, max: Infinity },
)
const shownLabel = computed(() =>
  notEmpty(props.label) ? props.label : props.coordinateAxis.toUpperCase(),
)
const arrowStep = computed(() => (isRelative.value ? 0.001 : 1))
</script>
