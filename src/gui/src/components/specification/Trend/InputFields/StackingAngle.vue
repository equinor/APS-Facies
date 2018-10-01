<template>
  <storable-numeric-field
    :grf-id="grfId"
    property-type="angle"
    sub-property-type="stacking"
    value-type="stacking"
    label="Stacking angle"
    unit="°"
    trend
  />
</template>

<script>
import VueTypes from 'vue-types'
import StorableNumericField from '@/components/specification/StorableNumericField'

export default {
  components: {
    StorableNumericField,
  },

  props: {
    grfId: VueTypes.string.isRequired,
  },

}
</script>
