<template>
  <v-expansion-panel
    :value="0"
  >
    <v-expansion-panel-content>
      <div slot="header">
        <h2>Truncation Rules</h2>
      </div>
      <truncation-header/>
      <v-layout row>
        <v-flex xs12>
          <component
            :is="truncationRuleComponent"
          />
        </v-flex>
      </v-layout>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import { mapState } from 'vuex'

import BayfillSpecification from '@/components/specification/TruncationRule/Bayfill'
import TruncationHeader from '@/components/specification/TruncationRule/header'

export default {
  components: {
    TruncationHeader,
  },

  computed: {
    ...mapState({
      truncationRuleType: state => state.truncationRules.templates.types.available[state.truncationRules.preset.type]
    }),
    truncationRuleComponent () {
      const mapping = {
        'Cubic': null,
        'Non-cubic': null,
        'Bayfill': BayfillSpecification,
      }
      return this.truncationRuleType
        ? mapping[this.truncationRuleType.name]
        : null
    },
  },
}
</script>
