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

import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import { TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'
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
  P extends PolygonSpecification = PolygonSpecification,
> extends Vue {
  waitingForSimulation = false

  @Prop({ required: true })
  readonly value: TruncationRule<T, S, P>

  get _allFaciesUsed (): boolean { return usesAllFacies({ rootGetters: this.$store.getters }, this.value) }

  get _canSimulateAllTrends (): boolean {
    return (
      this.value
      && !this.value.fields
        .some(field => (
          field.trend
          && field.trend.use
          && TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION.includes(field.trend.type))
        )
    )
  }

  get canSimulate (): boolean {
    return (
      this.value
      && this.value.ready
      && this._allFaciesUsed
      && this._canSimulateAllTrends
    )
  }

  get _explanation (): string | undefined {
    if (!this.value) return 'No truncation rule has been specified'
    if (!this._allFaciesUsed) return 'More facies are selected, than are used'
    if (!this._canSimulateAllTrends) {
      return `Some Gaussian Random Field uses a trend that cannot be simulated in the previewer (${
        TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION
          .reduce((prev: string, curr: string) => `${prev}${prev ? ', ' : ''}'${curr}'`, '')
      })`
    }
    if (!this.value.ready) return this.value.errorMessage
    return undefined
  }

  async refresh (): Promise<void> {
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
