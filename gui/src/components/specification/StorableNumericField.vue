<template>
  <numeric-field
    v-model="propertyValue"
    :value-type="valueType"
    :label="label"
    :unit="unit"
    :fmu-updatable="fmuUpdatable"
    :strictly-greater="strictlyGreater"
    :allow-negative="allowNegative"
    :ranges="ranges"
    :arrow-step="arrowStep"
    :use-modulus="useModulus"
    :enforce-ranges="enforceRanges"
    @update:error="(e: boolean) => emit('update:error', e)"
  />
</template>

<script setup lang="ts">
import { MinMax } from '@/api/types'
import { Optional } from '@/utils/typing'
import { GaussianRandomField } from '@/utils/domain'
import Trend from '@/utils/domain/gaussianRandomField/trend'
import Variogram from '@/utils/domain/gaussianRandomField/variogram'

import NumericField from '@/components/selection/NumericField.vue'

import { hasOwnProperty } from '@/utils/helpers'
import { computed } from 'vue'
import { useStore } from '../../store'

function getValue(
  field: Trend | Variogram,
  property: string,
  subProperty: string | undefined,
): any {
  return hasOwnProperty(field[property], subProperty)
    ? field[property][subProperty]
    : field[property]
}

type Props = {
  value: GaussianRandomField
  propertyType: string
  subPropertyType?: string
  label?: string
  valueType?: string
  unit?: string
  strictlyGreater?: boolean
  allowNegative?: boolean
  useModulus?: boolean
  trend?: boolean
  arrowStep?: number
  ranges?: Optional<MinMax>
  enforceRanges?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  subPropertyType: undefined,
  label: '',
  valueType: '',
  unit: '',
  strictlyGreater: false,
  allowNegative: false,
  useModulus: false,
  trend: false,
  arrowStep: 1,
  ranges: null,
  enforceRanges: false,
})
const store = useStore()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const field = computed(() => props.value[variogramOrTrend.value])

const propertyValue = computed({
  get: () => getValue(field.value, props.propertyType, props.subPropertyType),
  set: (value: any) =>
    store.dispatch(`gaussianRandomFields/${props.propertyType}`, {
      field: props.value,
      variogramOrTrend: variogramOrTrend.value,
      type: props.subPropertyType,
      value,
    }),
})

const fmuUpdatable = computed(() =>
  hasOwnProperty(propertyValue.value, 'updatable'),
)

const variogramOrTrend = computed(() => (props.trend ? 'trend' : 'variogram'))
</script>
