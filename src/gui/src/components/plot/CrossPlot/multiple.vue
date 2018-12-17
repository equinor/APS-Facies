<template>
  <v-container
    grid-list-md
    text-xs-center
  >
    <v-flex xs12>
      <h3>Cross plots</h3>
    </v-flex>
    <v-container
      align-center
      row
      wrap
    >
      <v-layout
        row
      >
        <v-flex xs12>
          <v-select
            v-model="selected"
            :items="available"
            label="Gaussian Fields to be used"
            multiple
          />
        </v-flex>
      </v-layout>
      <v-layout
        row
        wrap
        align-center
        justify-space-around
      >
        <v-flex
          v-for="(pair, index) in combinations"
          :key="index"
        >
          <cross-plot
            :value="pair"
          />
        </v-flex>
      </v-layout>
    </v-container>
  </v-container>
</template>

<script>
import VueTypes from 'vue-types'

import { AppTypes } from '@/utils/typing'

import CrossPlot from './index'

export default {
  components: {
    CrossPlot,
  },

  props: {
    value: VueTypes.arrayOf(AppTypes.gaussianRandomField).isRequired,
  },

  data () {
    return {
      selected: []
    }
  },

  computed: {
    available () {
      return this.value.map(field => {
        return {
          value: field.id,
          text: field.name,
        }
      })
    },
    combinations () {
      const pairs = []
      const available = this.selected
      if (!available) return pairs
      for (let i = 0; i < available.length; i++) {
        for (let j = i + 1; j < available.length; j++) {
          pairs.push([available[`${i}`], available[`${j}`]])
        }
      }
      return pairs
    },
  },

  watch: {
    available (value) {
      if (this.selected.some(selectedItem => value.indexOf(availableItem => availableItem.value === selectedItem.value) === -1)) {
        // That is, if there is some selected value that is no longer available
        this.selected = this.available.filter(availableItem => this.selected.some(selectedItem => selectedItem.value === availableItem.value))
      }
    }
  },

  beforeMount () {
    if (this.selected.length === 0 && this.value.length >= 2) {
      this.value.slice(0, 2).forEach(field => this.selected.push(field.id))
    }
  },
}
</script>
