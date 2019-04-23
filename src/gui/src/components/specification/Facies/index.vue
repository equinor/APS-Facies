<template>
  <facies-specification-base
    :value="value.facies"
    :disable="disable"
    @input.capture="facies => updateFacies(facies)"
  />
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

import { RootGetters } from '@/utils/helpers/store/typing'
import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import Polygon from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import FaciesSpecificationBase from './base.vue'

import { updateFacies } from '@/store/utils'

@Component({
  components: {
    FaciesSpecificationBase,
  }
})
export default class FaciesSpecification extends Vue {
  @Prop({ required: true })
  readonly value: Polygon

  @Prop({ required: true })
  readonly rule: TruncationRule<Polygon>

  @Prop({ default: false })
  readonly disable: ((facies: Facies) => boolean) | boolean

  async updateFacies (faciesId: ID) {
    const facies = (this.$store.getters as RootGetters)['facies/byId'](faciesId)
    await updateFacies(this.$store.dispatch, this.rule, this.value, facies, false)
  }
}
</script>
