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
import { AppTypes } from '@/utils/typing'
import StorableNumericField from '@/components/specification/StorableNumericField'

export default {
  components: {
    StorableNumericField,
  },

  props: {
    grfId: AppTypes.id.isRequired,
  },

}
</script>
