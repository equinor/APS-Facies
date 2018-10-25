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
