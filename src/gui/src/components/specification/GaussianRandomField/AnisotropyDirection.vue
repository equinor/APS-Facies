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
import VueTypes from 'vue-types'
import StorableNumericField from '@/components/specification/StorableNumericField'

export default {
  components: {
    azimuthAngle: StorableNumericField,
    dipAngle: StorableNumericField,
  },

  props: {
    grfId: VueTypes.string.isRequired,
  },

  computed: {
    propertyType () { return 'angle' },
  },
}
</script>
