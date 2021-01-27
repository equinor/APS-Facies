<template>
  <facies-specification
    :value="value"
    :rule="rule"
    :disable="facies => overlayFacies(facies)"
  />
</template>

<script lang="ts">
import FaciesSpecification from '@/components/specification/Facies/index.vue'

import { Bayfill, Facies, Polygon, TruncationRule } from '@/utils/domain'
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({
  components: {
    FaciesSpecification,
  }
})
export default class BackgroundFaciesSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: Polygon

  @Prop({ required: true })
  readonly rule!: TruncationRule

  overlayFacies (facies: Facies): boolean {
    if (this.rule instanceof Bayfill) {
      return false
    } else {
      return this.rule.isUsedInOverlay(facies)
    }
  }
}
</script>
