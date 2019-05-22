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
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

@Component({
  components: {
    FaciesSpecification,
  }
})
export default class OverlayFaciesSpecification<T extends Polygon, P extends PolygonSpecification> extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayPolygon

  @Prop({ required: true })
  readonly rule!: OverlayTruncationRule<T, P>

  backgroundFacies (facies: Facies) {
    return this.rule.isUsedInBackground(facies)
  }
}
</script>
