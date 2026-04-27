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
import type { MinMax } from '@/api/types'
import type { Optional } from '@/utils/typing'
import type { GaussianRandomField } from '@/utils/domain'
import type Trend from '@/utils/domain/gaussianRandomField/trend'
import type Variogram from '@/utils/domain/gaussianRandomField/variogram'

import NumericField from '@/components/selection/NumericField.vue'

import { hasOwnProperty } from '@/utils/helpers'
import { computed } from 'vue'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import type { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable.ts'

function getValue<
  T extends Trend | Variogram,
  PROPERTY extends keyof T,
  SUB_PROPERTY extends keyof T[keyof T] | undefined,
>(
  field: T,
  property: PROPERTY,
  subProperty?: SUB_PROPERTY,
): number | FmuUpdatable<number> | null {
  const value =
    !!subProperty && hasOwnProperty(field[property], subProperty)
      ? field[property][subProperty]
      : field[property]
  if (typeof value === 'string') {
    throw new Error('')
  }
  // @ts-expect-error
  return value
}

type TrendProps<T extends Trend = Trend> = {
  trend?: true
  propertyType: keyof T
  subPropertyType?: keyof T[keyof T]
}
type VariogramProps<T extends Variogram = Variogram> = {
  trend?: false
  propertyType: keyof T
  subPropertyType?: keyof T[keyof T]
}

type Props = (TrendProps | VariogramProps) & {
  value: GaussianRandomField
  trend?: boolean
  label: string
  valueType?: string
  unit?: string
  strictlyGreater?: boolean
  allowNegative?: boolean
  useModulus?: boolean
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
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const fieldStore = useGaussianRandomFieldStore()

const variogramOrTrend = computed(() => (props.trend ? 'trend' : 'variogram'))
const field = computed(() => props.value[variogramOrTrend.value])

// #257: Move all this logic outside this form input component.
// This belongs in gui/src/components/specification/GaussianRandomField/index.vue
const propertyValue = computed({
  get: () =>
    getValue(
      field.value,
      props.propertyType as keyof typeof field.value,
      props.subPropertyType,
    ),
  set: (value) =>
    fieldStore.setProperty(
      props.value,
      variogramOrTrend.value,
      props.propertyType as keyof typeof field.value,
      props.subPropertyType,
      // @ts-expect-error: Should work as expected
      value,
    ),
})

const fmuUpdatable = computed(() =>
  hasOwnProperty(propertyValue.value, 'updatable'),
)
</script>
