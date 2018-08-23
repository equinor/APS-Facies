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
      <v-flex>
        <v-text-field
          ref="input"
          :value="fieldValue"
          :error-messages="errors"
          :label="label"
          :suffix="unit"
          :disabled="disabled"
          @input="e => updateValue(e)"
          @blur="$v.fieldValue.$touch()"
          @keydown.up="increase"
          @keydown.down="decrease"
        />
      </v-flex>
      <v-flex
        v-if="isFmuUpdatable"
        v-bind="binding"
      >
        <v-checkbox
          v-model="updatable"
          hint="fmu"
          persistent-hint
          @change="e => setUpdatable(e)"
        />
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'
import {required as requiredField, between, numeric} from 'vuelidate/lib/validators'
import {updatableType, nullableNumber} from 'Utils/typing'
import {notEmpty, isEmpty} from 'Utils'

export default Vue.extend({
  props: {
    label: VueTypes.string.isRequired,
    valueType: VueTypes.string.def(''),
    slider: VueTypes.bool.def(false),
    value: VueTypes.oneOfType([nullableNumber, updatableType]),
    unit: VueTypes.string.def(''),
    optional: VueTypes.bool.def(false),
    discrete: VueTypes.bool.def(false),
    disabled: VueTypes.bool.def(false),
    fmuUpdatable: VueTypes.bool.def(false),
    allowNegative: VueTypes.bool.def(false),
    strictlyGreater: VueTypes.bool.def(false),
    strictlySmaller: VueTypes.bool.def(false),
    useModulus: VueTypes.bool.def(false),
    steps: VueTypes.number.def(10000),
    arrowStep: VueTypes.number.def(1),
    ranges: VueTypes.oneOfType([VueTypes.shape({
      min: VueTypes.number.isRequired,
      max: VueTypes.number.isRequired,
    }), null])
  },

  data () {
    return {
      fieldValue: this.getValue(this.value),
      updatable: this.getUpdatable(this.value),
    }
  },

  validations () {
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
    sliderValue: {
      get () { return (this.fieldValue - this.min) * this.steps / (this.max - this.min) },
      set (val) { this.fieldValue = val / this.steps * (this.max - this.min) + this.min },
    },
    constants () {
      return notEmpty(this.ranges)
        ? this.ranges
        : this.valueType !== '' && this.$store.state.constants.ranges.hasOwnProperty(this.valueType)
          ? this.$store.state.constants.ranges[this.valueType]
          : {max: Infinity, min: this.allowNegative ? -Infinity : 0}
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
      this.fieldValue = this.getValue(value)
      this.updatable = this.getUpdatable(value)
    }
  },

  methods: {
    setUpdatable (event) {
      this.emitChange(event)
    },
    emitChange (value) {
      const payload = this.value === null || typeof this.value.value === 'undefined'
        ? Number(value)
        : typeof value === 'boolean'
          ? {value: Number(this.fieldValue), updatable: value}
          : {value: Number(value), updatable: this.updatable}
      this.$v.fieldValue.$touch()
      this.$emit('input', payload)
    },
    updateValue (event) {
      let value = typeof event === 'string' ? event : event.target.value
      value = value.replace(',', '.')
      if (value === '.') {
        value = '0.'
      }
      let numericValue = this.getValue(this.value)
      if (/^[+-]?\d+(\.\d*)?$/.test(value)) {
        numericValue = Number(value)
        if (this.modulus) {
          numericValue = numericValue % this.max
        } else if (numericValue < this.min) {
          numericValue = this.min
        } else if (numericValue > this.max) {
          numericValue = this.max
        }
      } else if (value === '') {
        value = null
      } else if (value === '-') {
        value = '-'
      } else {
        value = this.value.value
        // FIXME: Hack to make sure illegal values are not displayed in the text field
        this.$refs.input.lazyValue = value
      }
      this.fieldValue = value
      this.emitChange(numericValue)
    },
    getValue (val) {
      return isEmpty(val)
        ? null
        : typeof val.value !== 'undefined'
          ? val.value
          : val
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
      this.fieldValue = String(Number(this.fieldValue) + this.arrowStep)
      this.emitChange(this.fieldValue)
    },
    decrease () {
      this.fieldValue = String(Number(this.fieldValue) - this.arrowStep)
      this.emitChange(this.fieldValue)
    },
  },
})
</script>
