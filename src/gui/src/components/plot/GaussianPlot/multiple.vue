<template>
  <v-container
    grid-list-md
    text-xs-center
  >
    <v-flex xs12>
      <h3>Gaussian Random Fields</h3>
    </v-flex>
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
        <v-layout
          column
          align-center
        >
          <v-flex>
            <h5>{{ field.name }}</h5>
          </v-flex>
          <v-flex>
            <gaussian-plot
              :data="field._data"
            />
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import VueTypes from 'vue-types'

import GaussianPlot from './index'
import { AppTypes } from '@/utils/typing'

export default {
  name: 'MultipleGaussianPlots',

  components: {
    GaussianPlot,
  },

  props: {
    value: VueTypes.arrayOf(AppTypes.gaussianRandomField).isRequired,
  }
}
</script>

<style scoped>

</style>
