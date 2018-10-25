<template>
  <div>
    <main-range
      :grf-id="grfId"
      :property-type="propertyType"
      sub-property-type="main"
      label="Parallel to Azimuth"
      unit="m"
      strictly-greater
    />
    <perpendicular-range
      :grf-id="grfId"
      :property-type="propertyType"
      sub-property-type="perpendicular"
      label="Normal to Azimuth"
      unit="m"
      strictly-greater
    />
    <vertical-range
      :grf-id="grfId"
      :property-type="propertyType"
      sub-property-type="vertical"
      label="Vertical (normal to dip)"
      unit="m"
      strictly-greater
    />
  </div>
</template>

<script>
import { AppTypes } from '@/utils/typing'
import StorableNumericField from '@/components/specification/StorableNumericField'

export default {
  components: {
    MainRange: StorableNumericField,
    PerpendicularRange: StorableNumericField,
    VerticalRange: StorableNumericField,
  },

  props: {
    grfId: AppTypes.id.isRequired,
  },

  computed: {
    propertyType () { return 'range' },
  },
}
</script>
