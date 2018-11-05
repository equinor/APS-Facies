<template>
  <div>
    <realization-map
      :data="data"
      :color-scale="faciesColors"
    />
    <wait-btn
      :waiting="waitingForSimulation"
      title="Refresh"
      @click="refresh"
    />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

import api from '@/api/rms'

import RealizationMap from '@/components/plot/GaussianPlot'

import { makeTruncationRuleSpecification } from '@/utils'
import WaitBtn from '@/components/baseComponents/WaitButton'

export default {
  name: 'FaciesRealization',
  components: {
    WaitBtn,
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
