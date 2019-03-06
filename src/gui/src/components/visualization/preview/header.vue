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

<script>
import IconButton from '@/components/selection/IconButton'

export default {
  name: 'PreviewHeader',

  components: {
    IconButton
  },

  data () {
    return {
      waitingForSimulation: false,
    }
  },

  computed: {
    rule () { return this.$store.getters.truncationRule },
    canSimulate () {
      return this.rule && this.rule.ready
    },
  },

  methods: {
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
}
</script>
