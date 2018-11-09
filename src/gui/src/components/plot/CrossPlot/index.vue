<template>
  <static-plot
    :data-definition="dataDefinition"
    :axis-names="{ x: field.name, y: other.name }"
  />
</template>

<script>
import StaticPlot from '@/components/plot/StaticPlot'
import VueTypes from 'vue-types'
import { GaussianRandomField } from '@/store/utils/domain/index'

const flatten = (arr) => {
  // TODO: Should be superfluous when Array.prototype.flat is part of ECMAScript
  return arr.reduce((flat, a) => flat.concat(a))
}

export default {
  components: {
    StaticPlot
  },

  props: {
    value: VueTypes.arrayOf(VueTypes.instanceOf(GaussianRandomField)).isRequired,
  },

  computed: {
    field () { return this.value[0] },
    other () { return this.value[1] },
    dataDefinition () {
      return [{
        type: 'scattergl',
        mode: 'markers',
        marker: { size: 1 },
        // TODO: Use Array.prototype.flat when possible
        x: flatten(this.field._data),
        y: flatten(this.other._data),
      }]
    },
  },
}
</script>

<style scoped>

</style>
