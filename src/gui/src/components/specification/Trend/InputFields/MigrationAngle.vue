<template>
  <storable-numeric-field
    :grf-id="grfId"
    label="Migration angle"
    property-type="angle"
    sub-property-type="migration"
    value-type="migration"
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
