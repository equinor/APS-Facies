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
    propertyType () { return 'power' }
  }
}
</script>
