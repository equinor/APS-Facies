<template>
  <storable-numeric-field
    :grf-id="grfId"
    :property-type="propertyType"
    :ranges="ranges"
    :sub-property-type="coordinateAxis"
    :label="shownLabel"
    :arrow-step="arrowStep"
    allow-negative
    trend
  />
</template>

<script>
import VueTypes from 'vue-types'
import StorableNumericField from '@/components/specification/StorableNumericField'
import { notEmpty } from '@/utils'
import { AppTypes } from '@/utils/typing'

export default {
  components: {
    StorableNumericField
  },

  props: {
    grfId: AppTypes.id.isRequired,
    originType: {
      required: true,
      type: String,
    },
    coordinateAxis: {
      required: true,
      type: String,
    },
    label: VueTypes.string.def(''),
  },

  computed: {
    propertyType () { return 'origin' },
    isRelative () { return this.originType === 'RELATIVE' },
    ranges () { return this.isRelative ? { min: 0, max: 1 } : { min: -Infinity, max: Infinity } },
    shownLabel () { return notEmpty(this.label) ? this.label : this.coordinateAxis.toUpperCase() },
    arrowStep () { return this.isRelative ? 0.001 : 1 },
  },
}
</script>
