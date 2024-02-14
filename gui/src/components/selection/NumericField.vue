<template>
  <v-row
    class="fill-height"
    align="center"
    justify="center"
    no-gutters
    :class="__class"
  >
    <v-col
      :cols="12 - (isFmuUpdatable ? checkboxSize + 1 : 0)"
      :class="__class"
    >
      <v-text-field
        ref="input"
        :class="__class"
        :value="fieldValue"
        :error-messages="errors"
        :label="label"
        :suffix="_unit"
        :disabled="disabled"
        :readonly="readonly"
        :hint="hint"
        :persistent-hint="persistentHint"
        :append-icon="appendIcon"
        @input.capture="(e: InputEvent) => updateValue(e)"
        @keydown.up="increase"
        @keydown.down="decrease"
        @click:append="(e: MouseEvent) => emit('click:append', e)"
        @update:error="(e: boolean) => propagateError(e)"
      />
      <!-- @blur="$v.fieldValue.$touch()" -->
    </v-col>
    <v-col v-if="isFmuUpdatable" v-bind="binding">
      <v-checkbox
        v-model="updatable"
        v-tooltip.bottom="`Toggle whether this should be updatable in FMU`"
        :class="__class"
        :disabled="disabled"
        persistent-hint
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts" generic="T extends number = number">
/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-use-before-define */

import { BigNumber } from 'mathjs'
import { isNumber } from 'lodash'

import math from '@/plugins/mathjs'

import { MinMax } from '@/api/types'
import { Optional } from '@/utils/typing'
import { notEmpty, isEmpty } from '@/utils'
import { hasOwnProperty } from '@/utils/helpers'

import type { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import { computed, ref, watch, onMounted } from 'vue'
import { useStore } from '../../store'
import type { ValidationRule } from '@vuelidate/core'
import useVuelidate from '@vuelidate/core'
import { VTextField } from 'vuetify/lib/components/index.mjs'
import { between, numeric, requiredUnless } from '@vuelidate/validators'
import { useInvalidation } from '@/utils/invalidation'

interface AdditionalRule {
  name: string
  check: (value: number) => boolean
  error: string
}

type InternalValue = BigNumber | number | string | null

type Props = {
  modelValue: FmuUpdatable<T> | number | null
  label: string
  valueType?: string
  unit?: string
  hint?: string
  appendIcon?: string
  persistentHint?: boolean
  optional?: boolean
  discrete?: boolean
  disabled?: boolean
  fmuUpdatable?: boolean
  allowNegative?: boolean
  strictlyGreater?: boolean
  strictlySmaller?: boolean
  useModulus?: boolean
  dense?: boolean
  enforceRanges?: boolean
  ignoreErrors?: boolean
  readonly?: boolean
  ranges?: Optional<MinMax>
  additionalRules?: AdditionalRule[]
  arrowStep?: number
}
const props = withDefaults(defineProps<Props>(), {
  valueType: '',
  unit: '',
  hint: '',
  appendIcon: '',
  persistentHint: false,
  optional: false,
  discrete: false,
  disabled: false,
  fmuUpdatable: false,
  allowNegative: false,
  strictlyGreater: false,
  strictlySmaller: false,
  useModulus: false,
  dense: false,
  enforceRanges: false,
  ignoreErrors: false,
  readonly: false,
  ranges: null,
  additionalRules: () => [],
  arrowStep: 1,
})
const emit = defineEmits<{
  (event: 'update:model-value', value: FmuUpdatableValue<T> | number): void
  (event: 'update:error', error: boolean): void
  (event: 'click:append', value: MouseEvent): void
}>()
const store = useStore()
const inputElement = ref<InstanceType<typeof VTextField> | null>(null)
const fieldValue = ref<InternalValue>(null)

const validators = computed(() => {
  const fieldValue: Record<string, ValidationRule> = {
    required: requiredUnless(props.optional),
    between: between(min, max),
    discrete: props.discrete ? numeric : () => true,
    strictlyGreater: props.strictlyGreater
      ? (value: number) => value > min.value
      : () => true,
    strictlySmaller: props.strictlySmaller
      ? (value: number) => value < max.value
      : () => true,
  }
  props.additionalRules.forEach((rule: AdditionalRule) => {
    fieldValue[rule.name] = (value: number) => rule.check(value)
  })

  return { fieldValue }
})

const v = useVuelidate(validators, { fieldValue })
useInvalidation(v)

function getUpdatable(val: FmuUpdatableValue | number | null): boolean {
  const defaultValue = false
  return isEmpty(val)
    ? defaultValue
    : val instanceof FmuUpdatableValue
    ? val.updatable
    : defaultValue
}
const updatable = computed({
  get: () => {
    const defaultValue = false
    return isEmpty(props.modelValue)
      ? defaultValue
      : props.modelValue instanceof FmuUpdatableValue
      ? props.modelValue.updatable
      : defaultValue
  },
  set: (value: boolean) => emitChange(value),
})

const constants = computed<MinMax>(() =>
  notEmpty(props.ranges)
    ? props.ranges
    : props.valueType !== '' &&
      hasOwnProperty(store.state.constants.ranges, props.valueType)
    ? store.state.constants.ranges[props.valueType]
    : { max: Infinity, min: props.allowNegative ? -Infinity : 0 },
)

const _unit = computed(() => {
  if (props.discrete) {
    if (!props.unit) return ''
    const irregular = {}
    return props.modelValue === 1
      ? props.unit
      : hasOwnProperty(irregular, props.unit)
      ? irregular[props.unit]
      : `${props.unit}s`
  } else {
    return props.unit
  }
})

const __class = computed(() => (props.dense ? ['dense'] : []))

const max = computed(() => constants.value.max)
const min = computed(() => constants.value.min)

const isFmuUpdatable = computed(
  () =>
    props.fmuUpdatable &&
    store.getters.fmuUpdatable &&
    (props.modelValue instanceof FmuUpdatableValue ||
      (props.modelValue !== null &&
        hasOwnProperty(props.modelValue, 'updatable'))),
)

const errors = computed<string[]>(() => {
  if (!v.value.fieldValue || props.ignoreErrors) return []
  if (!v.value.fieldValue.$dirty) return []
  return (v.value.fieldValue.$errors.map(error => {
    switch (error.$validator) {
      case 'required':
        return 'Is required'
      case 'discrete':
        return 'Must be a whole number'
      case 'between':
        return (
        max.value === Infinity
          ? `Must be greater than ${min.value}`
          : min.value === -Infinity
          ? `Must be smaller than ${max.value}`
          : `Must be between [${min.value}, ${max.value}]`
      )
      case 'strictlyGreater':
        return `Must be strictly greater than ${min.value}`
      case 'strictlySmaller':
        return `Must be strictly smaller than ${max.value}`
      default:
        return error.$message as string
    }
  }))
})

const checkboxSize = computed(() =>
  ['X', 'Y', 'Z'].includes(props.label) ? 2 : 1,
)

const binding = computed(() => ({ cols: checkboxSize.value.toString(10) }))

watch(props, ({ modelValue }: Props) => {
  if (hasChanged(modelValue)) {
    fieldValue.value = getValue(modelValue)
  }
})
onMounted(() => {
  fieldValue.value = getValue(props.modelValue)
})

function hasChanged(value: BigNumber | FmuUpdatableValue): boolean {
  // Helper method to deal with letting the '.' appear in the textfield
  // Returns this.fieldValue != value, in the proper types
  try {
    return math.unequal(
      // Not sure why it won't allow this...
      math.bignumber(fieldValue.value),
      getValue(value) ?? 0,
    ) as boolean
  } catch (e) {
    return false
  }
}

function emitChange(value: BigNumber | boolean | null): void {
  const payload =
    props.modelValue === null || !hasOwnProperty(props.modelValue, 'value')
      ? Number(value)
      : typeof value === 'boolean'
      ? { value: Number(fieldValue.value), updatable: value }
      : { value: Number(value), updatable: updatable.value }

  if ($v.fieldValue) $v.fieldValue.$touch()

  emit(
    'update:model-value',
    props.fmuUpdatable ? new FmuUpdatableValue(payload) : payload,
  )
}

function updateValue(value: BigNumber | string | InputEvent): void {
  if (value instanceof InputEvent) {
    value = (value.target as HTMLInputElement).value
  }

  if (typeof value === 'string') {
    value = value.replace(',', '.')
    value = value.replace(/[^\d.+-]*/g, '')
    if (/^[+-].*$/.test(value))
      value = value[0] + value.slice(1).replace(/[+-]/g, '')
    if (value.length >= 1) {
      if (value[0] === '+') value = value.slice(1)
      if (value[0] === '.') value = '0' + value
    }
  }

  let numericValue = getValue(value)
  if (/^[+-]?(\d+(\.\d*)?|\.\d+)$/.test(value.toString())) {
    numericValue = getValue(value)
  } else if (value === '') {
    // @ts-ignore
    value = null
    numericValue = null
  } else if (value === '-') {
    value = '-'
  } else if (value === '+') {
    value = ''
  } else {
    // @ts-ignore
    value =
      props.modelValue instanceof FmuUpdatableValue
        ? props.modelValue.value
        : props.modelValue
    // Hack to make sure illegal values are not displayed in the text field
    // @ts-ignore
    inputElement.lazyValue = value
  }
  if (/^[+-]?\d+\.0*$/.test((value || '').toString())) {
    fieldValue.value = value
  } else if (/^[+-]?\d+\.\d+0+$/.test((value || '').toString())) {
    fieldValue.value = (numericValue || 0).toFixed(
      (value || '').toString().split('.')[1].length,
    )
  } else if (/^[+-]$/.test((value || '').toString())) {
    fieldValue.value = value
    numericValue = null
  } else {
    fieldValue.value = numericValue
  }
  emitChange(numericValue)
}

function getValue(value: FmuUpdatableValue | InternalValue): BigNumber | null {
  if (value === null) return null
  if (isEmpty(value) && !isNumber(value)) return null
  if (value instanceof FmuUpdatableValue) value = value.value
  if (value === '-') value = 0
  if (props.useModulus) {
    if (math.larger(value, max.value)) value = min.value
    else if (math.smaller(value, min.value)) value = max.value
  }
  if (typeof value === 'string') {
    value = math.bignumber(value)
  }
  if (props.enforceRanges) {
    if (value < min.value) value = min.value
    if (value > max.value) value = max.value
  }
  return math.bignumber(value)
}

function increase(): void {
  if (props.readonly) return
  updateValue(
    math.add(
      math.bignumber(fieldValue.value),
      math.bignumber(props.arrowStep),
    ) as BigNumber,
  )
}

function decrease(): void {
  if (props.readonly) return
  updateValue(
    math.subtract(
      math.bignumber(fieldValue.value),
      math.bignumber(props.arrowStep),
    ) as BigNumber,
  )
}

function propagateError(error: boolean): void {
  if (props.ignoreErrors) {
    error = false
  }
  emit('update:error', error)
}

watch(props, (value: Props) => {
  if (!value.ignoreErrors) v.value.$touch()
})

watch(errors, () => {
  emit('update:error', errors.value.length > 0)
})
</script>
