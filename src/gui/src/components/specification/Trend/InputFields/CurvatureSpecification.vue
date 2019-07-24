<template>
  <storable-numeric-field
    :value="value"
    property-type="curvature"
    value-type="curvature"
    label="Curvature of ellipse"
    strictly-greater
    :ranges="{ min: minCurvature, max: Number.POSITIVE_INFINITY }"
    trend
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
export default class CurvatureSpecification extends Vue {
  @Prop({ required: true })
  readonly value: GaussianRandomField

  get minCurvature () {
    const field = this.value
    return field && field.trend && field.trend.type === 'HYPERBOLIC'
      ? 1
      : 0
  }
}
</script>
