<template>
  <facies-specification-base
    :value="value.facies"
    :disable="disable"
    :clearable="clearable"
    @input.capture="facies => updateFacies(facies)"
  />
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

import { Store } from '@/store/typing'
import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import FaciesSpecificationBase from './base.vue'

@Component({
  components: {
    FaciesSpecificationBase,
  }
})
export default class FaciesSpecification<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> extends Vue {
  @Prop({ required: true })
  readonly value: Polygon

  @Prop({ required: true })
  readonly rule: TruncationRule<T, S, P>

  @Prop({ default: false, type: Boolean })
  readonly clearable!: boolean

  @Prop({ default: false })
  readonly disable: ((facies: Facies) => boolean) | boolean

  async updateFacies (faciesId: ID | undefined): Promise<void> {
    const facies = (this.$store as Store).getters['facies/byId'](faciesId)
    await this.$store.dispatch('truncationRules/updateFacies', {
      rule: this.rule,
      polygon: this.value,
      facies,
    })
  }
}
</script>
