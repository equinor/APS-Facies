<template>
  <div>
    <azimuth-angle
      :grf-id="grfId"
      :property-type="propertyType"
      sub-property-type="azimuth"
      value-type="azimuth"
      label="Azimuth"
      unit="°"
      use-modulus
    />
    <dip-angle
      :grf-id="grfId"
      :property-type="propertyType"
      sub-property-type="dip"
      value-type="dip"
      label="Dip"
      unit="°"
    />
  </div>
</template>

<script>
import { AppTypes } from '@/utils/typing'
import StorableNumericField from '@/components/specification/StorableNumericField'

export default {
  components: {
    azimuthAngle: StorableNumericField,
    dipAngle: StorableNumericField,
  },

  props: {
    grfId: AppTypes.id.isRequired,
  },

  computed: {
    propertyType () { return 'angle' },
  },
}
</script>
