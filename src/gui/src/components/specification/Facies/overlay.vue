<template>
  <facies-specification
    :value="value"
    :rule="rule"
    :disable="facies => backgroundFacies(facies)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import FaciesSpecification from '@/components/specification/Facies/index.vue'

import { OverlayPolygon, Polygon, Facies } from '@/utils/domain'
import { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

@Component({
  components: {
    FaciesSpecification,
  }
})
export default class OverlayFaciesSpecification<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayPolygon

  @Prop({ required: true })
  readonly rule!: OverlayTruncationRule<T, S, P>

  backgroundFacies (facies: Facies): boolean {
    return this.rule.isUsedInBackground(facies)
  }
}
</script>
