<template>
  <v-layout>
    <v-flex
      v-for="(pair, index) in combinations"
      :key="index"
    >
      <cross-plot
        :value="pair"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import VueTypes from 'vue-types'

import { GaussianRandomField } from '@/store/utils/domain'

import CrossPlot from './index'

export default {
  components: {
    CrossPlot,
  },

  props: {
    value: VueTypes.arrayOf(VueTypes.instanceOf(GaussianRandomField)).isRequired,
  },

  computed: {
    combinations () {
      const pairs = []
      if (!this.value) return pairs
      for (let i = 0; i < this.value.length; i++) {
        for (let j = i + 1; j < this.value.length; j++) {
          pairs.push([this.value[`${i}`], this.value[`${j}`]])
        }
      }
      return pairs
    },
  }
}
</script>
