<template>
  <storable-numeric-field
    :value="value"
    :property-type="propertyType"
    :ranges="ranges"
    :sub-property-type="coordinateAxis"
    :label="shownLabel"
    :arrow-step="arrowStep"
    allow-negative
    trend
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

import { notEmpty } from '@/utils'

@Component({
  components: {
    StorableNumericField,
  },
})
export default class CoordinateSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  @Prop({ required: true })
  readonly originType: string

  @Prop({ required: true })
  readonly coordinateAxis!: string

  @Prop({ default: '' })
  readonly label!: string

  get propertyType () { return 'origin' }

  get isRelative () { return this.originType === 'RELATIVE' }

  get ranges () { return this.isRelative ? { min: 0, max: 1 } : { min: -Infinity, max: Infinity } }

  get shownLabel () { return notEmpty(this.label) ? this.label : this.coordinateAxis.toUpperCase() }

  get arrowStep () { return this.isRelative ? 0.001 : 1 }
}
</script>
