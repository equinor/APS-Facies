<template>
  <div>
    <main-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="main"
      label="Parallel to Azimuth"
      unit="m"
      strictly-greater
    />
    <perpendicular-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="perpendicular"
      label="Normal to Azimuth"
      unit="m"
      strictly-greater
    />
    <vertical-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="vertical"
      label="Vertical (normal to dip)"
      unit="m"
      strictly-greater
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

@Component({
  components: {
    MainRange: StorableNumericField,
    PerpendicularRange: StorableNumericField,
    VerticalRange: StorableNumericField,
  },
})
export default class RangeSpecification extends Vue {
  @Prop({ required: true })
  readonly value: GaussianRandomField

  get propertyType () { return 'range' }
}
</script>
