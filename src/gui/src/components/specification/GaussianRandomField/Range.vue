<template>
  <div>
    <main-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="main"
      label="Parallel to Azimuth"
      unit="m"
      strictly-greater
      @update:error="e => update('main', e)"
    />
    <perpendicular-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="perpendicular"
      label="Normal to Azimuth"
      unit="m"
      strictly-greater
      @update:error="e => update('perpendicular', e)"
    />
    <vertical-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="vertical"
      label="Vertical (normal to dip)"
      unit="m"
      strictly-greater
      @update:error="e => update('vertical', e)"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

interface Invalid {
  main: boolean
  perpendicular: boolean
  vertical: boolean
}

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

  invalid: Invalid = {
    main: false,
    perpendicular: false,
    vertical: false,
  }

  get propertyType () { return 'range' }

  @Watch('invalid', { deep: true })
  onInvalidChanged ({ vertical, perpendicular, main }: Invalid) {
    this.$emit('update:error', vertical || perpendicular || main)
  }

  update (type: string, value: boolean) {
    Vue.set(this.invalid, type, value)
  }
}
</script>
