<template>
  <v-popover
    bottom
    :disabled="canSimulate"
    trigger="hover"
  >
    <icon-button
      :disabled="!canSimulate"
      :waiting="waitingForSimulation"
      icon="refresh"
      @click="refresh"
    />
    <template slot="popover">
      {{ _explanation }}
    </template>
  </v-popover>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import IconButton from '@/components/selection/IconButton.vue'

import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import { usesAllFacies } from '@/store/utils/helpers'

import { displayError } from '@/utils/helpers/storeInteraction'

@Component({
  components: {
    IconButton
  },
})
export default class PreviewHeader<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
> extends Vue {
  waitingForSimulation: boolean = false

  @Prop({ required: true })
  readonly value: TruncationRule<T, S>

  get _allFaciesUsed () { return usesAllFacies({ rootGetters: this.$store.getters }, this.value) }

  get canSimulate () {
    return (
      this.value
      && this.value.ready
      && this._allFaciesUsed
    )
  }

  get _explanation (): string | undefined {
    if (!this.value) return 'No truncation rule has been specified'
    if (!this._allFaciesUsed) return 'More facies are selected, than are used'
    if (!this.value.ready) return this.value.errorMessage
    return undefined
  }

  async refresh () {
    await this.$store.dispatch('facies/normalize')
    this.waitingForSimulation = true
    try {
      await this.$store.dispatch('truncationRules/updateRealization', this.value)
    } catch (e) {
      await displayError(e)
    } finally {
      this.waitingForSimulation = false
    }
  }
}
</script>
