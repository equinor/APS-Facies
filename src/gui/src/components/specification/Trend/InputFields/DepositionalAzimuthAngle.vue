<template>
  <storable-numeric-field
    :grf-id="grfId"
    label="Azimuth (depositional)"
    property-type="angle"
    sub-property-type="azimuth"
    value-type="depositionalAzimuth"
    unit="°"
    trend
    use-modulus
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
