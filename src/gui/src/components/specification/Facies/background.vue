<template>
  <facies-specification-base
    :value="value.group"
    :rule="rule"
    multiple
    @input.capture="facies => updateBackgroundFacies(facies)"
  />

</template>

<script>
import VueTypes from 'vue-types'

import FaciesSpecificationBase from './base'

import { TruncationRule } from '@/store/utils/domain'

import { AppTypes } from '@/utils/typing'

export default {
  name: 'FaciesSpecification',

  components: {
    FaciesSpecificationBase,
  },

  props: {
    rule: VueTypes.instanceOf(TruncationRule).isRequired,
    value: VueTypes.shape({
      group: AppTypes.ids.isRequired,
    }).loose.isRequired,
  },

  computed: {
  },
  methods: {
    updateBackgroundFacies (facies) {
      return this.$store.dispatch('truncationRules/updateBackgroundFacies', { rule: this.rule, polygon: this.value, facies })
    },
  },
}
</script>
