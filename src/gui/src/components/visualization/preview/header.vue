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
import { Component, Vue } from 'vue-property-decorator'

import IconButton from '@/components/selection/IconButton.vue'

@Component({
  components: {
    IconButton
  },
})
export default class PreviewHeader extends Vue {
  waitingForSimulation: boolean = false

  get rule () { return this.$store.getters.truncationRule }
  get canSimulate () { return this.rule && this.rule.ready }

  async refresh () {
    await this.$store.dispatch('facies/normalize')
    this.waitingForSimulation = true
    try {
      await this.$store.dispatch('truncationRules/updateRealization', this.rule)
    } catch (e) {
      alert(e)
    }
    this.waitingForSimulation = false
  }
}
</script>
