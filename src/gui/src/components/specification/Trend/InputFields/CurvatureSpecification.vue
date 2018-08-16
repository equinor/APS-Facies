<template>
  <storable-numeric-field
    :grf-id="grfId"
    property-type="curvature"
    value-type="curvature"
    label="Curvature of ellipse"
    strictly-greater
    trend
  />
</template>

<script>
import VueTypes from 'vue-types'
import StorableNumericField from 'Components/specification/StorableNumericField'

export default {
  components: {
    StorableNumericField,
  },

  props: {
    grfId: VueTypes.string.isRequired,
  },

}
</script>
