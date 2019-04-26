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
  />
</template>

<script>
import VueTypes from 'vue-types'
import NumericField from '@/components/selection/NumericField'
import { AppTypes } from '@/utils/typing'

const getValue = (field, property, subProperty) => {
  return field[`${property}`].hasOwnProperty(subProperty)
    ? field[`${property}`][`${subProperty}`]
    : field[`${property}`]
}

export default {
  components: {
    NumericField
  },

  props: {
    grfId: AppTypes.id.isRequired,
    propertyType: {
      required: true,
      type: String,
    },
    subPropertyType: VueTypes.string.def(''),
    label: VueTypes.string.def(''),
    valueType: VueTypes.string.def(''),
    unit: VueTypes.string.def(''),
    strictlyGreater: VueTypes.bool.def(false),
    allowNegative: VueTypes.bool.def(false),
    useModulus: VueTypes.bool.def(false),
    arrowStep: VueTypes.number.def(1),
    ranges: VueTypes.oneOfType([VueTypes.shape({
      min: VueTypes.number.isRequired,
      max: VueTypes.number.isRequired,
    }), null]),
    trend: VueTypes.bool.def(false),
  },

  computed: {
    field () { return this.$store.state.gaussianRandomFields.fields[this.grfId][this.variogramOrTrend] },
    propertyValue: {
      get: function () { return this.getValue() },
      set: function (value) { this.dispatchChange(value) },
    },
    fmuUpdatable () { return this.propertyValue.hasOwnProperty('updatable') },
    variogramOrTrend () { return this.trend ? 'trend' : 'variogram' },
  },

  methods: {
    dispatchChange (value) {
      this.$store.dispatch('gaussianRandomFields/' + this.propertyType, { grfId: this.grfId, variogramOrTrend: this.variogramOrTrend, type: this.subPropertyType, value })
    },
    getValue () {
      return getValue(this.field, this.propertyType, this.subPropertyType)
    }
  },
}
</script>
