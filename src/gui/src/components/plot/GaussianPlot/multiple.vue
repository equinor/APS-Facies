<template>
  <v-layout
    row
    wrap
    xs12
  >
    <v-flex
      v-for="field in value"
      :key="field.id"
      column
    >
      <v-flex xs12>
        <h5>{{ field.name }}</h5>
      </v-flex>
      <v-flex xs12>
        <gaussian-plot
          :data="field._data"
        />
      </v-flex>
    </v-flex>
  </v-layout>
</template>

<script>
import VueTypes from 'vue-types'

import GaussianPlot from './index'
import { GaussianRandomField } from '@/store/utils/domain'

export default {
  name: 'MultipleGaussianPlots',

  components: {
    GaussianPlot,
  },

  props: {
    value: VueTypes.arrayOf(VueTypes.instanceOf(GaussianRandomField)).isRequired,
  }
}
</script>

<style scoped>

</style>
