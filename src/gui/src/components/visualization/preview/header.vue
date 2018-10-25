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
      this.waitingForSimulation = true
      await this.$store.dispatch('truncationRules/updateRealization', this.rule)
      this.waitingForSimulation = false
    }
  }
}
</script>
