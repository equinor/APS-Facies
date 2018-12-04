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
