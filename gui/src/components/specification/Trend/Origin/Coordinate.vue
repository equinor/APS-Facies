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
    @update:error="e => propagateError(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import { MinMax } from '@/api/types'

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

  get propertyType (): string { return 'origin' }

  get isRelative (): boolean { return this.originType === 'RELATIVE' }

  get ranges (): MinMax { return this.isRelative ? { min: 0, max: 1 } : { min: -Infinity, max: Infinity } }

  get shownLabel (): string { return notEmpty(this.label) ? this.label : this.coordinateAxis.toUpperCase() }

  get arrowStep (): number { return this.isRelative ? 0.001 : 1 }

  propagateError (value: boolean): void {
    this.$emit('update:error', value)
  }
}
</script>
