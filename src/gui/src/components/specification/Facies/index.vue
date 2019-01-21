<template>
  <facies-specification-base
    :value="value.facies"
    :rule="rule"
    :disable="disable"
    @input.capture="facies => updateFacies(facies)"
  />
</template>

<script>
import VueTypes from 'vue-types'

import FaciesSpecificationBase from './base'

import { updateFacies } from '@/store/utils'
import { AppTypes } from '@/utils/typing'

export default {
  name: 'FaciesSpecification',

  components: {
    FaciesSpecificationBase,
  },

  props: {
    rule: AppTypes.truncationRule.isRequired,
    value: VueTypes.shape({
      facies: AppTypes.id.isRequired,
    }).loose.isRequired,
    disable: VueTypes.func.def(() => false),
  },

  computed: {
  },
  methods: {
    updateFacies (faciesId) {
      updateFacies(this.$store.dispatch, this.rule, this.value, faciesId, false)
    },
  },
}
</script>
