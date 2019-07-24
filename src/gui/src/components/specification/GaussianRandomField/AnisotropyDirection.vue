<template>
  <div>
    <azimuth-angle
      :value="value"
      :property-type="propertyType"
      sub-property-type="azimuth"
      value-type="azimuth"
      label="Azimuth"
      unit="°"
      use-modulus
    />
    <dip-angle
      :value="value"
      :property-type="propertyType"
      sub-property-type="dip"
      value-type="dip"
      label="Dip"
      unit="°"
      use-modulus
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

import { GaussianRandomField } from '@/utils/domain'

@Component({
  components: {
    azimuthAngle: StorableNumericField,
    dipAngle: StorableNumericField,
  },
})
export default class AnisotropyDirection extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get propertyType () { return 'angle' }
}
</script>
