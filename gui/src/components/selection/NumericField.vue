<template>
  <v-row
    class="fill-height"
    align="center"
    justify="center"
    no-gutters
    :class="__class"
  >
    <v-col
      :cols="fmuUpdatable ? 10 : 12"
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
        @input.capture="e => updateValue(e)"
        @blur="$v.fieldValue.$touch()"
        @keydown.up="increase"
        @keydown.down="decrease"
        @click:append="e => $emit('click:append', e)"
        @update:error="e => propagateError(e)"
      />
    </v-col>
    <v-col
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
    </v-col>
  </v-row>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-use-before-define */
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { BigNumber } from 'mathjs'
import { isNumber } from 'lodash'

import { required as requiredField, between, numeric } from 'vuelidate/lib/validators'

import math from '@/plugins/mathjs'

import { MinMax } from '@/api/types'
import { Optional } from '@/utils/typing'
import { notEmpty, isEmpty } from '@/utils'
import { hasOwnProperty } from '@/utils/helpers'

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
      required: (this as NumericField).optional ? true : requiredField,
      between: between((this as NumericField).min, (this as NumericField).max),
      discrete: (this as NumericField).discrete ? numeric : true,
      strictlyGreater: (this as NumericField).strictlyGreater ? (value: number): boolean => value > (this as NumericField).min : true,
      strictlySmaller: (this as NumericField).strictlySmaller ? (value: number): boolean => value < (this as NumericField).max : true,
      // TODO: Add option to add more validations
    }
    ;(this as NumericField).additionalRules.forEach((rule: AdditionalRule) => {
      fieldValue[`${rule.name}`] = (value: number): boolean => rule.check(value)
    })
    return {
      fieldValue: {
        required: (this as NumericField).optional ? true : requiredField,
        between: between((this as NumericField).min, (this as NumericField).max),
        discrete: (this as NumericField).discrete ? numeric : true,
        strictlyGreater: (this as NumericField).strictlyGreater ? (value: number): boolean => value > (this as NumericField).min : true,
        strictlySmaller: (this as NumericField).strictlySmaller ? (value: number): boolean => value < (this as NumericField).max : true,
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

  @Prop({ default: false, type: Boolean })
  readonly ignoreErrors!: boolean

  @Prop({ default: false, type: Boolean })
  readonly readonly!: boolean

  @Prop({ default: null })
  readonly ranges!: Optional<MinMax>

  @Prop({ default: () => [] })
  readonly additionalRules!: AdditionalRule[]

  @Prop({ default: 1 })
  readonly arrowStep!: number

  fieldValue: InternalValue = null

  get updatable (): boolean { return NumericField.getUpdatable(this.value) }
  set updatable (value) { this.setUpdatable(value) }

  get constants (): { max: number, min: number } {
    return notEmpty(this.ranges)
      ? this.ranges
      : this.valueType !== '' && hasOwnProperty(this.$store.state.constants.ranges, this.valueType)
        ? this.$store.state.constants.ranges[this.valueType]
        : { max: Infinity, min: this.allowNegative ? -Infinity : 0 }
  }

  get _unit (): string {
    if (this.discrete) {
      if (!this.unit) return ''
      const irregular = {
      }
      return this.value === 1
        ? this.unit
        : hasOwnProperty(irregular, this.unit)
          ? irregular[this.unit]
          : `${this.unit}s`
    } else {
      return this.unit
    }
  }

  // eslint-disable-next-line @typescript-eslint/naming-convention
  get __class (): string[] {
    const classes: string[] = []
    if (this.dense) classes.push('dense')
    return classes
  }

  get max (): number { return this.constants.max }
  get min (): number { return this.constants.min }

  get isFmuUpdatable (): boolean {
    return this.fmuUpdatable
      && this.$store.getters.fmuUpdatable
      && (
        this.value instanceof FmuUpdatableValue
        || (this.value !== null && hasOwnProperty(this.value, 'updatable')
        )
      )
  }

  get errors (): string[] {
    if (!this.$v.fieldValue || this.ignoreErrors) return []
    const errors: string[] = []
    if (!this.$v.fieldValue.$dirty) return errors
    !this.$v.fieldValue.required && errors.push('Is required')
    !this.$v.fieldValue.discrete && errors.push('Must be a whole number')
    !this.$v.fieldValue.between && errors.push(
      this.max === Infinity
        ? `Must be greater than ${this.min}`
        : this.min === -Infinity
          ? `Must be smaller than ${this.max}`
          : `Must be between [${this.min}, ${this.max}]`
    )
    !this.$v.fieldValue.strictlyGreater && errors.push(`Must be strictly greater than ${this.min}`)
    !this.$v.fieldValue.strictlySmaller && errors.push(`Must be strictly smaller than ${this.max}`)
    this.additionalRules.forEach(rule => {
      // @ts-ignore
      !this.$v.fieldValue[`${rule.name}`] && errors.push(rule.error)
    })
    return errors
  }

  get binding (): { [_: string]: string } {
    const binding: { [_: string]: string } = {}
    // FIXME: Hack to adjust the checkboxes for Origin coordinates
    binding.cols = (['X', 'Y', 'Z'].indexOf(this.label) !== -1)
      ? '2'
      : '1'
    return binding
  }

  @Watch('value')
  onValueChange (value: FmuUpdatableValue | BigNumber): void {
    if (this.hasChanged(value)) {
      this.fieldValue = this.getValue(value)
    }
  }

  mounted (): void {
    this.fieldValue = this.getValue(this.value)
  }

  hasChanged (value: BigNumber | FmuUpdatableValue): boolean {
    // Helper method to deal with letting the '.' appear in the textfield
    // Returns this.fieldValue != value, in the proper types
    try {
      return (math.unequal(math.bignumber(this.fieldValue), (this.getValue(value) || 0)) as boolean)
    } catch (e) {
      return false
    }
  }

  setUpdatable (event: boolean): void {
    this.emitChange(!!event)
  }

  emitChange (value: BigNumber | boolean | null): void {
    const payload = this.value === null || !hasOwnProperty(this.value, 'value')
      ? Number(value)
      : typeof value === 'boolean'
        ? { value: Number(this.fieldValue), updatable: value }
        : { value: Number(value), updatable: this.updatable }
    this.$v.fieldValue && this.$v.fieldValue.$touch()
    this.$emit('input', this.fmuUpdatable ? new FmuUpdatableValue(payload) : payload)
  }

  updateValue (value: BigNumber | string): void {
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
    if (this.readonly) return
    this.updateValue((math.add(math.bignumber(this.fieldValue), math.bignumber(this.arrowStep))) as BigNumber)
  }

  decrease (): void {
    if (this.readonly) return
    this.updateValue((math.subtract(math.bignumber(this.fieldValue), math.bignumber(this.arrowStep)) as BigNumber))
  }

  propagateError (error: boolean): void {
    if (this.ignoreErrors) {
      error = false
    }
    this.$emit('update:error', error)
  }

  @Watch('ignoreErrors')
  onIgnoreErrorChange (ignoreErrors: boolean): void {
    if (!ignoreErrors) {
      this.$v.$touch()
    }
  }
}
</script>
