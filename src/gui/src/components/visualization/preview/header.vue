<template>
  <v-layout
    row
    align-center
    justify-end
  >
    <v-flex>
      <icon-button
        :disabled="!canSimulate"
        :waiting="waitingForSimulation"
        icon="refresh"
        @click="refresh"
      />
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import IconButton from '@/components/selection/IconButton.vue'

import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import { usesAllFacies } from '@/store/utils/helpers'

import { ErrorMessage } from '@/utils/domain/messages'

@Component({
  components: {
    IconButton
  },
})
export default class PreviewHeader<T extends Polygon, S extends PolygonSerialization> extends Vue {
  waitingForSimulation: boolean = false

  @Prop({ required: true })
  readonly value: TruncationRule<T, S>

  get canSimulate () {
    return (
      this.value
      && this.value.ready
      && usesAllFacies({ rootGetters: this.$store.getters }, this.value)
    )
  }

  async refresh () {
    await this.$store.dispatch('facies/normalize')
    this.waitingForSimulation = true
    try {
      await this.$store.dispatch('truncationRules/updateRealization', this.value)
    } catch (e) {
      this.$store.dispatch('message/change', new ErrorMessage(e))
    } finally {
      this.waitingForSimulation = false
    }
  }
}
</script>
