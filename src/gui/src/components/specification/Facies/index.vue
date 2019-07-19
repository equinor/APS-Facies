<template>
  <facies-specification-base
    :value="value.facies"
    :disable="disable"
    @input.capture="facies => updateFacies(facies)"
  />
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

import { Store } from '@/store/typing'
import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import FaciesSpecificationBase from './base.vue'

@Component({
  components: {
    FaciesSpecificationBase,
  }
})
export default class FaciesSpecification<
  P extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
> extends Vue {
  @Prop({ required: true })
  readonly value: Polygon

  @Prop({ required: true })
  readonly rule: TruncationRule<P, S>

  @Prop({ default: false })
  readonly disable: ((facies: Facies) => boolean) | boolean

  async updateFacies (faciesId: ID) {
    const facies = (this.$store as Store).getters['facies/byId'](faciesId)
    if (facies) {
      await this.$store.dispatch('truncationRules/updateFacies', {
        rule: this.rule,
        polygon: this.value,
        facies,
      })
    }
  }
}
</script>
