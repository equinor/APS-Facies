<template>
  <div>
    <realization-map
      :data="data"
      :color-scale="faciesColors"
    />
    <v-btn
      @click="refresh"
    >
      <span v-if="!waitingForSimulation">Refresh</span>
      <span v-else><v-progress-circular indeterminate/></span>
    </v-btn>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import api from '@/api/rms'

import RealizationMap from '@/components/plot/GaussianPlot'

import { makeTruncationRuleSpecification } from '@/utils'

export default {
  name: 'FaciesRealization',
  components: {
    RealizationMap: RealizationMap,
  },

  data () {
    return {
      waitingForSimulation: false,
      data: [],
    }
  },

  computed: {
    ...mapGetters({
      rule: 'truncationRule',
      fields: 'fields',
    }),
    fields () {
      const fields = this.$store.getters.fields
      return this.rule
        ? this.rule.fields.map(({ field, channel }) => {
          return {
            channel,
            field: field ? fields[`${field}`] : null
          }
        })
        : null
    },
    faciesColors () {
      return this.$store.getters.faciesTable
        .map(facies => {
          return {
            value: facies.code,
            color: facies.color,
          }
        })
    }
  },

  methods: {
    async refresh () {
      this.waitingForSimulation = true
      this.data = await api.simulateRealization(this.fields, makeTruncationRuleSpecification(this.rule, this.$store.getters))
      this.waitingForSimulation = false
    }
  }
}
</script>

<style scoped>

</style>
