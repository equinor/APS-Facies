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
