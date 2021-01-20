<template>
  <numeric-field
    v-model="propertyValue"
    :value-type="valueType"
    :label="label"
    :unit="unit"
    :fmu-updatable="fmuUpdatable"
    :strictly-greater="strictlyGreater"
    :allow-negative="allowNegative"
    :ranges="ranges"
    :arrow-step="arrowStep"
    :use-modulus="useModulus"
    @update:error="e => propagateError(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { MinMax } from '@/api/types'
import { Optional } from '@/utils/typing'
import { GaussianRandomField } from '@/utils/domain'
import Trend from '@/utils/domain/gaussianRandomField/trend'
import Variogram from '@/utils/domain/gaussianRandomField/variogram'

import NumericField from '@/components/selection/NumericField.vue'

import { hasOwnProperty } from '@/utils/helpers'

function getValue (field: Variogram | Trend, property: string, subProperty: string): any {
  return hasOwnProperty(field[`${property}`], subProperty)
    ? field[`${property}`][`${subProperty}`]
    : field[`${property}`]
}

@Component({
  components: {
    NumericField,
  },
})
export default class StorableNumericField extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  @Prop({ required: true })
  readonly propertyType!: string

  @Prop({ default: '' })
  readonly subPropertyType!: string

  @Prop({ default: '' })
  readonly label!: string

  @Prop({ default: '' })
  readonly valueType!: string

  @Prop({ default: '' })
  readonly unit!: string

  @Prop({ default: false, type: Boolean })
  readonly strictlyGreater!: boolean

  @Prop({ default: false, type: Boolean })
  readonly allowNegative!: boolean

  @Prop({ default: false, type: Boolean })
  readonly useModulus!: boolean

  @Prop({ default: false, type: Boolean })
  readonly trend!: boolean

  @Prop({ default: 1 })
  readonly arrowStep!: number

  @Prop()
  readonly ranges!: Optional<MinMax>

  get field (): Trend | Variogram { return this.value[this.variogramOrTrend] }

  get propertyValue (): any { return this.getValue() }
  set propertyValue (value) { this.dispatchChange(value) }

  get fmuUpdatable (): boolean { return hasOwnProperty(this.propertyValue, 'updatable') }

  get variogramOrTrend (): 'trend' | 'variogram' { return this.trend ? 'trend' : 'variogram' }

  dispatchChange (value: number): void {
    this.$store.dispatch(`gaussianRandomFields/${this.propertyType}`, { field: this.value, variogramOrTrend: this.variogramOrTrend, type: this.subPropertyType, value })
  }

  getValue (): any {
    return getValue(this.field, this.propertyType, this.subPropertyType)
  }

  propagateError (value: boolean): void {
    this.$emit('update:error', value)
  }
}
</script>
