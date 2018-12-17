<template>
  <v-container
    grid-list-md
    text-xs-center
    ma-0
    pa-0
  >
    <v-flex xs12>
      <h3>Gaussian Random Fields</h3>
    </v-flex>
    <v-layout
      row
      wrap
      xs12
      pa-0
      ma-0
    >
      <v-flex
        v-for="field in value"
        :key="field.id"
        :ref="`v-flex:${field.id}`"
        column
      >
        <v-layout
          column
          align-center
        >
          <h5>{{ field.name }}</h5>
          <gaussian-plot
            pa-0
            ma-0
            :data="field._data"
            :size="size"
          />
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
  },

  computed: {
    size: {
      cache: false,
      get () {
        return this.value
          .map(field => {
            if (Object.values(this.$refs).length > 0) {
              const el = this.$refs[`v-flex:${field.id}`][0].firstChild
              return {
                width: el.clientWidth,
                height: el.clientHeight,
              }
            } else {
              return {
                width: 100,
                height: 100,
              }
            }
          })
          .reduce((max, curr) => {
            const air = 0.1
            return {
              width: Math.floor(Math.max(max.width, curr.width) * (1 - air)),
              height: Math.floor(Math.max(max.height, curr.height) * (1 - air)),
            }
          })
      },
    },
  },
}
</script>
