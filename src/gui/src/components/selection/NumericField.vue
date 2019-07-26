<template>
  <v-layout
    align-center
    justify-center
    fill-height
    :class="__class"
  >
    <v-flex
      v-if="canShowSlider"
      xs8
    >
      <v-slider
        v-model="sliderValue"
        :disabled="disabled"
        :max="steps"
        :step="100/steps"
      />
    </v-flex>
    <v-flex
      v-if="canShowField"
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
        :hint="hint"
        :persistent-hint="persistentHint"
        :append-icon="appendIcon"
        @input.capture="e => updateValue(e)"
        @blur="$v.fieldValue.$touch()"
        @keydown.up="increase"
        @keydown.down="decrease"
        @click:append="e => $emit('click:append', e)"
        @update:error="e => propagateEvent('update:error', e)"
      />
    </v-flex>
    <v-flex
      v-if="isFmuUpdatable"
      v-bind="binding"
    >
      <v-checkbox
        v-model="updatable"
        v-tooltip.bottom="`Toggle whether this should be updatable in FMU`"
        :class="__class"
        :disabled="disabled"
        persistent-hint
      />
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { BigNumber } from 'mathjs'
import { isNumber } from 'lodash'

import { required as requiredField, between, numeric } from 'vuelidate/lib/validators'

import math from '@/plugins/mathjs'

import { MinMax } from '@/api/types'
import { Optional } from '@/utils/typing'
import { notEmpty, isEmpty } from '@/utils'

import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

interface AdditionalRule {
  name: string
  check: (value: number) => boolean
  error: string
}

type InternalValue = BigNumber | number | string | null

@Component({
  // @ts-ignore
  validations () {
    const fieldValue = {
      required: this.optional ? true : requiredField,
      between: between(this.min, this.max),
      discrete: this.discrete ? numeric : true,
      strictlyGreater: this.strictlyGreater ? (value: number) => value > this.min : true,
      strictlySmaller: this.strictlySmaller ? (value: number) => value < this.max : true,
      // TODO: Add option to add more validations
    }
    this.additionalRules.forEach((rule: AdditionalRule) => {
      fieldValue[`${rule.name}`] = (value: number) => rule.check(value)
    })
    return {
      fieldValue: {
        // @ts-ignore
        required: this.optional ? true : requiredField,
        // @ts-ignore
        between: between(this.min, this.max),
        // @ts-ignore
        discrete: this.discrete ? numeric : true,
        // @ts-ignore
        strictlyGreater: this.strictlyGreater ? (value: number) => value > this.min : true,
        // @ts-ignore
        strictlySmaller: this.strictlySmaller ? (value: number) => value < this.max : true,
      },
    }
  },

})
export default class NumericField extends Vue {
  @Prop({ required: true })
  readonly value!: FmuUpdatableValue | number | null

  @Prop({ required: true })
  readonly label!: string

  @Prop({ default: '' })
  readonly valueType!: string

  @Prop({ default: '' })
  readonly unit!: string

  @Prop({ default: '' })
  readonly hint!: string

  @Prop({ default: '' })
  readonly appendIcon!: string

  @Prop({ default: false, type: Boolean })
  readonly slider!: boolean

  @Prop({ default: false, type: Boolean })
  readonly onlySlider!: boolean

  @Prop({ default: false, type: Boolean })
  readonly persistentHint!: boolean

  @Prop({ default: false, type: Boolean })
  readonly optional!: boolean

  @Prop({ default: false, type: Boolean })
  readonly discrete!: boolean

  @Prop({ default: false, type: Boolean })
  readonly disabled!: boolean

  @Prop({ default: false, type: Boolean })
  readonly fmuUpdatable!: boolean

  @Prop({ default: false, type: Boolean })
  readonly allowNegative!: boolean

  @Prop({ default: false, type: Boolean })
  readonly strictlyGreater!: boolean

  @Prop({ default: false, type: Boolean })
  readonly strictlySmaller!: boolean

  @Prop({ default: false, type: Boolean })
  readonly useModulus!: boolean

  @Prop({ default: false, type: Boolean })
  readonly dense!: boolean

  @Prop({ default: false, type: Boolean })
  readonly enforceRanges!: boolean

  @Prop({ default: null })
  readonly ranges!: Optional<MinMax>

  @Prop({ default: () => [] })
  readonly additionalRules!: AdditionalRule[]

  @Prop({ default: 10000 })
  readonly steps!: number

  @Prop({ default: 1 })
  readonly arrowStep!: number

  fieldValue: InternalValue = null

  get updatable () { return NumericField.getUpdatable(this.value) }
  set updatable (value) { this.setUpdatable(value) }

  // @ts-ignore
  get sliderValue () { return (this.fieldValue - this.min) * this.steps / (this.max - this.min) }
  set sliderValue (val) { this.fieldValue = val / this.steps * (this.max - this.min) + this.min }

  get constants () {
    return notEmpty(this.ranges)
      ? this.ranges
      : this.valueType !== '' && this.$store.state.constants.ranges.hasOwnProperty(this.valueType)
        ? this.$store.state.constants.ranges[this.valueType]
        : { max: Infinity, min: this.allowNegative ? -Infinity : 0 }
  }

  get _unit () {
    if (this.discrete) {
      if (!this.unit) return ''
      const irregular = {
      }
      return this.value === 1
        ? this.unit
        : irregular.hasOwnProperty(this.unit)
          ? irregular[this.unit]
          : `${this.unit}s`
    } else {
      return this.unit
    }
  }

  get __class (): string[] {
    const classes: string[] = []
    if (this.dense) classes.push('dense')
    return classes
  }

  get max (): number { return this.constants.max }
  get min (): number { return this.constants.min }

  get canShowSlider () { return this.slider && this.max < Infinity && this.min > -Infinity }
  get canShowField () { return this.canShowSlider ? !this.onlySlider : true }

  get isFmuUpdatable () {
    return this.fmuUpdatable
      && (
        this.value instanceof FmuUpdatableValue
        || (this.value !== null && this.value.hasOwnProperty('updatable')
        )
      )
  }

  get errors () {
    const errors: string[] = []
    // @ts-ignore
    if (!this.$v.fieldValue.$dirty) return errors
    // @ts-ignore
    !this.$v.fieldValue.required && errors.push('Is required')
    // @ts-ignore
    !this.$v.fieldValue.discrete && errors.push('Must be a whole number')
    // @ts-ignore
    !this.$v.fieldValue.between && errors.push(`Must be between [${this.min}, ${this.max}]`)
    // @ts-ignore
    !this.$v.fieldValue.strictlyGreater && errors.push(`Must be strictly greater than ${this.min}`)
    // @ts-ignore
    !this.$v.fieldValue.strictlySmaller && errors.push(`Must be strictly smaller than ${this.max}`)
    this.additionalRules.forEach(rule => {
      // @ts-ignore
      !this.$v.fieldValue[`${rule.name}`] && errors.push(rule.error)
    })
    return errors
  }

  get binding () {
    const binding: { [_: string]: boolean } = {}
    // FIXME: Hack to adjust the checkboxes for Origin coordinates
    if (['X', 'Y', 'Z'].indexOf(this.label) !== -1) binding.xs2 = true
    else binding.xs1 = true
    return binding
  }

  @Watch('value')
  onValueChange (value: FmuUpdatableValue | BigNumber) {
    if (this.hasChanged(value)) {
      this.fieldValue = this.getValue(value)
    }
  }

  mounted () {
    this.fieldValue = this.getValue(this.value)
  }

  hasChanged (value: BigNumber | FmuUpdatableValue) {
    // Helper method to deal with letting the '.' appear in the textfield
    // Returns this.fieldValue != value, in the proper types
    try {
      return math.unequal(math.bignumber(this.fieldValue), (this.getValue(value) || 0))
    } catch (e) {
      return false
    }
  }

  setUpdatable (event: boolean) {
    this.emitChange(!!event)
  }

  emitChange (value: BigNumber | boolean | null) {
    const payload = this.value === null || !this.value.hasOwnProperty('value')
      ? Number(value)
      : typeof value === 'boolean'
        ? { value: Number(this.fieldValue), updatable: value }
        : { value: Number(value), updatable: this.updatable }
    // @ts-ignore
    this.$v.fieldValue.$touch()
    this.$emit('input', this.fmuUpdatable ? new FmuUpdatableValue(payload) : payload)
  }

  updateValue (value: BigNumber | string) {
    // value may also be of type InputEvent, which is dealt with here
    // @ts-ignore
    if (typeof value.target !== 'undefined') {
      // An event has been passed
      // @ts-ignore
      value = value.target.value
    }
    if (typeof value === 'string') {
      value = value.replace(',', '.')
      value = value.replace(/[^\d.+-]*/g, '')
      if (/^[+-].*$/.test(value)) value = value[0] + value.slice(1).replace(/[+-]/g, '')
      if (value.length >= 1) {
        if (value[0] === '+') value = value.slice(1)
        if (value[0] === '.') value = '0' + value
      }
    }

    let numericValue = this.getValue(value)
    if (/^[+-]?(\d+(\.\d*)?|\.\d+)$/.test(value.toString())) {
      numericValue = this.getValue(value)
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
      value = this.value instanceof FmuUpdatableValue ? this.value.value : this.value
      // Hack to make sure illegal values are not displayed in the text field
      // @ts-ignore
      this.$refs.input.lazyValue = value
    }
    if (/^[+-]?\d+\.0*$/.test((value || '').toString())) {
      this.fieldValue = value
    } else if (/^[+-]?\d+\.\d+0+$/.test((value || '').toString())) {
      this.fieldValue = (numericValue || 0).toFixed((value || '').toString().split('.')[1].length)
    } else if (/^[+-]$/.test((value || '').toString())) {
      this.fieldValue = value
      numericValue = null
    } else {
      this.fieldValue = numericValue
    }
    this.emitChange(numericValue)
  }
  getValue (value: FmuUpdatableValue | InternalValue): BigNumber | null {
    if (value === null) return null
    if (isEmpty(value) && !isNumber(value)) return null
    if (value instanceof FmuUpdatableValue) value = value.value
    if (value === '-') value = 0
    if (this.useModulus) {
      if (math.larger(value, this.max)) value = this.min
      else if (math.smaller(value, this.min)) value = this.max
    }
    if (this.enforceRanges) {
      if (value < this.min) value = this.min
      if (value > this.max) value = this.max
    }
    return math.bignumber((value as number))
  }

  static getUpdatable (val: FmuUpdatableValue | number | null): boolean {
    const defaultValue = false
    return isEmpty(val)
      ? defaultValue
      : val instanceof FmuUpdatableValue
        ? val.updatable
        : defaultValue
  }

  increase (): void {
    this.updateValue((math.add(math.bignumber(this.fieldValue), math.bignumber(this.arrowStep))) as BigNumber)
  }

  decrease (): void {
    this.updateValue((math.subtract(math.bignumber(this.fieldValue), math.bignumber(this.arrowStep)) as BigNumber))
  }

  propagateEvent (type: string, value: boolean): void {
    this.$emit(type, value)
  }
}
</script>
