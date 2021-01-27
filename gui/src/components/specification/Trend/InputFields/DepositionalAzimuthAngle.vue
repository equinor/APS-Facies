<template>
  <storable-numeric-field
    :value="value"
    label="Azimuth (depositional)"
    property-type="angle"
    sub-property-type="azimuth"
    value-type="depositionalAzimuth"
    unit="°"
    trend
    use-modulus
    @update:error="e => propagateError(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

@Component({
  components: {
    StorableNumericField,
  },
})
export default class DepositionalAzimuthAngle extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  propagateError (value: boolean): void {
    this.$emit('update:error', value)
  }
}
</script>
