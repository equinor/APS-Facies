<template>
  <fraction-field
    :value="value.fraction"
    :disabled="disabled"
    @input="fraction => updateFactor(value, fraction)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'

import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'

@Component({
  components: {
    FractionField,
  },
})
export default class PolygonFractionField<T extends Polygon, S extends PolygonSerialization> extends Vue {
  @Prop({ required: true })
  readonly value!: T

  @Prop({ required: true })
  readonly rule!: TruncationRule<T, S>

  get disabled () { return !hasFaciesSpecifiedForMultiplePolygons(this.rule.polygons, this.value.facies) }

  async updateFactor (polygon: T, value: number) {
    await this.$store.dispatch(
      'truncationRules/changeProportionFactors',
      { rule: this.rule, polygon, value }, { root: true }
    )
  }
}
</script>
