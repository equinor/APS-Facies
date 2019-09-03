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
      @update:error="e => update('azimuth', e)"
    />
    <dip-angle
      :value="value"
      :property-type="propertyType"
      sub-property-type="dip"
      value-type="dip"
      label="Dip"
      unit="°"
      use-modulus
      @update:error="e => update('dip', e)"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

import { GaussianRandomField } from '@/utils/domain'

interface Invalid {
  azimuth: boolean
  dip: boolean
}

@Component({
  components: {
    azimuthAngle: StorableNumericField,
    dipAngle: StorableNumericField,
  },
})
export default class AnisotropyDirection extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  invalid: Invalid = {
    azimuth: false,
    dip: false,
  }

  get propertyType () { return 'angle' }

  @Watch('invalid', { deep: true })
  onInvalidChange ({ azimuth, dip }: Invalid) {
    this.$emit('update:error', azimuth || dip)
  }

  update (type: 'dip' | 'azimuth', value: boolean) {
    Vue.set(this.invalid, type, value)
  }
}
</script>
