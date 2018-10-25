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
import { AppTypes } from '@/utils/typing'
import StorableNumericField from '@/components/specification/StorableNumericField'

// TODO: Ensure the unit of '%' is correct, and consistent e.g. 100% -> 1
export default {
  components: {
    StorableNumericField,
  },

  props: {
    grfId: AppTypes.id.isRequired,
  },

}
</script>
