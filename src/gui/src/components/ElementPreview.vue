<template>
  <v-layout
    row
    wrap
  >
    <v-flex xs6>
      <h3>Truncation rule</h3>
      <truncation-map
        :truncation-rule-id="ruleId"
      />
    </v-flex>
    <v-flex xs6>
      <h3>Realization</h3>
      <facies-realization/>
    </v-flex>
    <v-flex xs12>
      <h3>Gaussian Random Fields</h3>
    </v-flex>
    <v-flex xs12>
      <h3>Cross plots</h3>
    </v-flex>
  </v-layout>
</template>

<script>
import TruncationMap from '@/components/plot/TruncationMap'
import FaciesRealization from '@/components/plot/FaciesRealization'

export default {
  components: {
    FaciesRealization,
    TruncationMap,
  },

  computed: {
    ruleId () {
      const rule = this.$store.getters.truncationRule
      return rule ? rule.id : ''
    }
  },
}
</script>
