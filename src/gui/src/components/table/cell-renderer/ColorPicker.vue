<template>
  <color-picker
    v-model="color"
    :colors="colors"
    :inline="true"
    popover-to="left"
    swatches-size="30"
  />
</template>

<script>
import Vue from 'vue'
import Swatches from 'vue-swatches'

import 'vue-swatches/dist/vue-swatches.min.css'

const apsPalette = [
  '#7cfc00', // lawngreen
  '#808080', // grey
  '#1e90ff', // dodgerblue
  '#ffd700', // gold
  '#9932cc', // darkorchid
  '#00ffff', // cyan
  '#b22222', // firebrick
  '#6b8e23', // olivedrab
  '#0000ff', // blue
  '#dc143c', // crimson
  '#ff8c00', // darkorange
  '#ff0000', // red
]

export default Vue.extend({
  components: {
    colorPicker: Swatches
  },
  data () {
    return {
      color: null,
      colors: apsPalette,
    }
  },

  created () {
    this.setColor(this.params)
  },

  methods: {
    getValue () {
      // TODO: Dispatch an action saying the facies table / a single facies has changed
      return this.color
    },
    isPopup () {
      return true
    },
    setColor (params) {
      this.color = params.value
    },
  }
})
</script>
