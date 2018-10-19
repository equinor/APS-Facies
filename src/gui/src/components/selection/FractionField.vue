<template>
  <numeric-field
    :value="value"
    :arrow-step="0.01"
    :ranges="ranges"
    :fmu-updatable="fmuUpdatable"
    label=""
    optional
    enforce-ranges
    @input="e => propagate(e)"
  />
</template>

<script>
import VueTypes from 'vue-types'

import { nullableNumber, updatableType } from '@/utils/typing'
import NumericField from '@/components/selection/NumericField'

export default {
  components: {
    NumericField,
  },

  props: {
    value: VueTypes.oneOfType([nullableNumber, updatableType]).isRequired,
    fmuUpdatable: VueTypes.bool.def(false),
  },

  computed: {
    ranges () {
      return {
        min: 0,
        max: 1,
      }
    }
  },

  methods: {
    propagate (value) {
      this.$emit('input', value)
    },
  },
}
</script>

<style scoped>

</style>
