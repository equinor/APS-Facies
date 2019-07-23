<template>
  <storable-numeric-field
    :grf-id="grfId"
    property-type="curvature"
    value-type="curvature"
    label="Curvature of ellipse"
    strictly-greater
    :ranges="{ min: minCurvature, max: Number.POSITIVE_INFINITY }"
    trend
  />
</template>

<script>
import { AppTypes } from '@/utils/typing'
import StorableNumericField from '@/components/specification/StorableNumericField'

export default {
  components: {
    StorableNumericField,
  },

  props: {
    grfId: AppTypes.id.isRequired,
  },

  computed: {
    minCurvature () {
      const field = this.$store.state.gaussianRandomFields.available[`${this.grfId}`]
      return field && field.trend && field.trend.type === 'HYPERBOLIC'
        ? 1
        : 0
    }
  },

}
</script>
