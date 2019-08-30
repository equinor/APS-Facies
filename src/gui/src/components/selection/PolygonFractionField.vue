<template>
  <fraction-field
    :value="value.fraction"
    :append-icon="appendIcon"
    :disabled="disabled"
    @input="fraction => updateFactor(value, fraction)"
    @click:append="normalizeFractions()"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'

import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { getId } from '@/utils'

@Component({
  components: {
    FractionField,
  },
})
export default class PolygonFractionField<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> extends Vue {
  @Prop({ required: true })
  readonly value!: T

  @Prop({ required: true })
  readonly rule!: TruncationRule<T, S, P>

  get disabled () {
    return (
      !hasFaciesSpecifiedForMultiplePolygons(this.rule.polygons, this.value.facies)
      || !this.value.facies
    )
  }

  get appendIcon () {
    return this.disabled || this.rule.isPolygonFractionsNormalized(this.value)
      ? ''
      // @ts-ignore
      : this.$vuetify.icons.values.refresh
  }

  async updateFactor (polygon: T, value: number) {
    await this.$store.dispatch(
      'truncationRules/changeProportionFactors',
      { rule: this.rule, polygon, value }, { root: true }
    )
  }

  async normalizeFractions () {
    const polygons: T[] = this.rule.polygons
      .filter((polygon: T): boolean => getId(polygon.facies) === getId(this.value.facies))
    const sum = polygons
      .reduce((sum, polygon): number => polygon.fraction + sum, 0)
    await Promise.all(polygons.map(polygon => this.updateFactor(polygon, polygon.fraction / sum)))
  }
}
</script>
