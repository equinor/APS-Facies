<template>
  <storable-numeric-field
    :grf-id="grfId"
    :arrow-step="0.01"
    :ranges="ranges"
    property-type="relativeStdDev"
    label="Relative std. dev."
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

  computed: {
    ranges () {
      return { min: 0, max: 1 }
    }
  }
}
</script>
