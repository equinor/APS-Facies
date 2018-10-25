<template>
  <static-plot
    :data-definition="dataDefinition"
    :expand="expand"
  />
</template>

<script>
import { mapGetters } from 'vuex'
import VueTypes from 'vue-types'

import StaticPlot from '@/components/plot/StaticPlot'

const filterOnCode = (data, code) => {
  return data
    .map(arr => arr.map(val => val === code ? 1 : null))
}

export default {
  name: 'FaciesRealization',
  components: {
    StaticPlot,
  },

  props: {
    expand: VueTypes.bool.def(false),
  },

  computed: {
    ...mapGetters({
      faciesTable: 'faciesTable',
      rule: 'truncationRule',
    }),
    dataDefinition () {
      return this.faciesTable
        .filter(({ selected }) => !!selected)
        .map(({ color, code }) => {
          return {
            z: filterOnCode(this.data, code),
            zsmooth: 'best',
            type: 'heatmap',
            hoverinfo: 'none',
            colorscale: [[0, color], [1, color]],
            showscale: false,
          }
        })
    },
    data () {
      return this.rule && this.rule._realization
        ? this.rule._realization
        : []
    },
  },
}
</script>
