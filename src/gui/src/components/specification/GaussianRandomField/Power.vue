<template>
  <storable-numeric-field
    :grf-id="grfId"
    :property-type="propertyType"
    value-type="power"
    label="Power"
    unit=""
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

  computed: {
    propertyType () { return 'power' }
  }
}
</script>
