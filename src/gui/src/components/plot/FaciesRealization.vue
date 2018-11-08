<template>
  <div>
    <realization-map
      :data="data"
      :color-scale="faciesColors"
    />
    <icon-button
      :disabled="!canSimulate"
      :waiting="waitingForSimulation"
      icon="refresh"
      @click="refresh"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import api from '@/api/rms'

import RealizationMap from '@/components/plot/GaussianPlot'

import { makeTruncationRuleSpecification } from '@/utils'
import IconButton from '@/components/selection/IconButton'

export default {
  name: 'FaciesRealization',
  components: {
    IconButton,
    RealizationMap,
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
    canSimulate () {
      return !!this.$store.getters.truncationRule
    },
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
      const data = await api.simulateRealization(this.fields, makeTruncationRuleSpecification(this.rule, this.$store.getters))
      this.data = data.faciesMap
      data.fields.forEach(field => {
        this.$store.dispatch('gaussianRandomFields/updateSimulationData', {
          grfId: Object.values(this.$store.getters.fields).find(item => item.name === field.name).id,
          data: field.data,
        })
      })
      this.waitingForSimulation = false
    }
  }
}
</script>

<style scoped>

</style>
