<template>
  <facies-specification-base
    :value="value.facies"
    @input.capture="facies => updateFacies(facies)"
  />
</template>

<script>
import VueTypes from 'vue-types'

import FaciesSpecificationBase from './base'

import { updateFacies } from '@/store/utils'
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
      facies: AppTypes.id.isRequired,
    }).loose.isRequired,
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
