<template>
  <storable-numeric-field
    :grf-id="grfId"
    property-type="relativeSize"
    label="Relative size of ellipse"
    unit="%"
    trend
  />
</template>

<script>
import VueTypes from 'vue-types'
import StorableNumericField from 'Components/specification/StorableNumericField'

// TODO: Ensure the unit of '%' is correct, and consistent e.g. 100% -> 1
export default {
  components: {
    StorableNumericField,
  },

  props: {
    grfId: VueTypes.string.isRequired,
  },

}
</script>
