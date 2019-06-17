<template>
  <div>
    <v-layout
      align-center
      justify-center
      row
      fill-height
    >
      <v-flex
        v-if="canShowSlider"
        xs8
      >
        <v-slider
          v-model="sliderValue"
          :max="steps"
          :step="100/steps"
        />
      </v-flex>
      <v-flex
        v-if="canShowField"
      >
        <v-text-field
          ref="input"
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
        />
      </v-flex>
      <v-flex
        v-if="isFmuUpdatable"
        v-bind="binding"
      >
        <v-tooltip bottom>
          <span slot="activator">
            <v-checkbox
              v-model="updatable"
              persistent-hint
            />
          </span>
          <span>Toggle whether "this field" should be updatable in FMU</span>
        </v-tooltip>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'

import math from 'mathjs'
import { isNumber } from 'lodash'

import { required as requiredField, between, numeric } from 'vuelidate/lib/validators'

import { updatableType, nullableNumber } from '@/utils/typing'
import { notEmpty, isEmpty } from '@/utils'

import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

math.config({
  number: 'BigNumber'
})

export default Vue.extend({
  props: {
    label: {
      required: true,
      type: String,
    },
    valueType: VueTypes.string.def(''),
    slider: VueTypes.bool.def(false),
    onlySlider: VueTypes.bool.def(false),
    value: VueTypes.oneOfType([nullableNumber, updatableType]),
    unit: VueTypes.string.def(''),
    hint: VueTypes.string.def(''),
    appendIcon: VueTypes.string.def(''),
    persistentHint: VueTypes.bool.def(false),
    optional: VueTypes.bool.def(false),
    discrete: VueTypes.bool.def(false),
    disabled: VueTypes.bool.def(false),
    fmuUpdatable: VueTypes.bool.def(false),
    allowNegative: VueTypes.bool.def(false),
    strictlyGreater: VueTypes.bool.def(false),
    strictlySmaller: VueTypes.bool.def(false),
    useModulus: VueTypes.bool.def(false),
    additionalRules: VueTypes.arrayOf(VueTypes.shape({
      name: VueTypes.string.isRequired,
      check: VueTypes.func.isRequired,
      error: VueTypes.string.isRequired,
    })).def([]),
    steps: VueTypes.number.def(10000),
    arrowStep: VueTypes.number.def(1),
    enforceRanges: VueTypes.bool.def(false),
    ranges: VueTypes.oneOfType([VueTypes.shape({
      min: VueTypes.number.isRequired,
      max: VueTypes.number.isRequired,
    }), null])
  },

  data () {
    return {
      fieldValue: this.getValue(this.value),
    }
  },

  validations () {
    const fieldValue = {
      required: this.optional ? true : requiredField,
      between: between(this.min, this.max),
      discrete: this.discrete ? numeric : true,
      strictlyGreater: this.strictlyGreater ? value => value > this.min : true,
      strictlySmaller: this.strictlySmaller ? value => value < this.max : true,
      // TODO: Add option to add more validations
    }
    this.additionalRules.forEach(rule => {
      fieldValue[`${rule.name}`] = value => rule.check(value)
    })
    return {
      fieldValue: {
        required: this.optional ? true : requiredField,
        between: between(this.min, this.max),
        discrete: this.discrete ? numeric : true,
        strictlyGreater: this.strictlyGreater ? value => value > this.min : true,
        strictlySmaller: this.strictlySmaller ? value => value < this.max : true,
      },
    }
  },

  computed: {
    updatable: {
      get: function () { return this.getUpdatable(this.value) },
      set: function (value) { this.setUpdatable(value) },
    },
    sliderValue: {
      get () { return (this.fieldValue - this.min) * this.steps / (this.max - this.min) },
      set (val) { this.fieldValue = val / this.steps * (this.max - this.min) + this.min },
    },
    constants () {
      return notEmpty(this.ranges)
        ? this.ranges
        : this.valueType !== '' && this.$store.state.constants.ranges.hasOwnProperty(this.valueType)
          ? this.$store.state.constants.ranges[this.valueType]
          : { max: Infinity, min: this.allowNegative ? -Infinity : 0 }
    },
    _unit () {
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
    },
    max () {
      return this.constants.max
    },
    min () {
      return this.constants.min
    },
    canShowSlider () {
      return this.slider && this.max < Infinity && this.min > -Infinity
    },
    canShowField () {
      return this.canShowSlider ? !this.onlySlider : true
    },
    isFmuUpdatable () {
      return this.fmuUpdatable && typeof this.value.updatable !== 'undefined'
    },
    errors () {
      const errors = []
      if (!this.$v.fieldValue.$dirty) return errors
      !this.$v.fieldValue.required && errors.push('Is required')
      !this.$v.fieldValue.discrete && errors.push('Must be a whole number')
      !this.$v.fieldValue.between && errors.push(`Must be between [${this.min}, ${this.max}]`)
      !this.$v.fieldValue.strictlyGreater && errors.push(`Must be strictly greater than ${this.min}`)
      !this.$v.fieldValue.strictlySmaller && errors.push(`Must be strictly smaller than ${this.max}`)
      this.additionalRules.forEach(rule => {
        !this.$v.fieldValue[`${rule.name}`] && errors.push(rule.error)
      })
      return errors
    },
    binding () {
      const binding = {}
      // FIXME: Hack to adjust the checkboxes for Origin coordinates
      if (['X', 'Y', 'Z'].indexOf(this.label) !== -1) binding.xs2 = true
      else binding.xs1 = true
      return binding
    },
  },

  watch: {
    value (value) {
      if (this.hasChanged(value)) {
        this.fieldValue = this.getValue(value)
      }
    }
  },

  methods: {
    hasChanged (value) {
      // Helper method to deal with letting the '.' appear in the textfield
      // Returns this.fieldValue != value, in the proper types
      return math.unequal(math.bignumber(this.fieldValue), this.getValue(value))
    },
    setUpdatable (event) {
      this.emitChange(!!event)
    },
    emitChange (value) {
      const payload = this.value === null || typeof this.value.value === 'undefined'
        ? Number(value)
        : typeof value === 'boolean'
          ? { value: Number(this.fieldValue), updatable: value }
          : { value: Number(value), updatable: this.updatable }
      this.$v.fieldValue.$touch()
      this.$emit('input', this.fmuUpdatable ? new FmuUpdatableValue(payload) : payload)
    },
    updateValue (value) {
      if (typeof value.target !== 'undefined') {
        // An event has been passed
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
      if (/^[+-]?(\d+(\.\d*)?|\.\d+)$/.test(value)) {
        numericValue = this.getValue(value)
      } else if (value === '') {
        value = null
        numericValue = null
      } else if (value === '-') {
        value = '-'
      } else if (value === '+') {
        value = ''
      } else {
        value = this.value ? this.value.value : this.value
        // Hack to make sure illegal values are not displayed in the text field
        this.$refs.input.lazyValue = value
      }
      if (/^[+-]?\d+\.0*$/.test(value)) {
        this.fieldValue = value
      } else if (/^[+-]?\d+\.\d+0+$/.test(value)) {
        this.fieldValue = numericValue.toFixed(value.split('.')[1].length)
      } else {
        this.fieldValue = numericValue
      }
      this.emitChange(numericValue)
    },
    getValue (value) {
      if (isEmpty(value) && !isNumber(value)) return null
      if (typeof value.value !== 'undefined') value = value.value
      if (this.modulus) value = math.mod(value, this.max)
      if (this.enforceRanges) {
        if (value < this.min) value = this.min
        if (value > this.max) value = this.max
      }
      return math.bignumber(value)
    },
    getUpdatable (val) {
      const defaultValue = false
      return isEmpty(val)
        ? defaultValue
        : typeof val.updatable !== 'undefined'
          ? val.updatable
          : defaultValue
    },
    increase () {
      this.updateValue(math.add(math.bignumber(this.fieldValue), math.bignumber(this.arrowStep)))
    },
    decrease () {
      this.updateValue(math.subtract(math.bignumber(this.fieldValue), math.bignumber(this.arrowStep)))
    },
  },
})
</script>
