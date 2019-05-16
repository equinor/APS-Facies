<template>
  <static-plot
    :data-definition="data.polygons"
    :annotations="data.annotations"
    :expand="expand"
    svg
  />
</template>

<script>
import VueTypes from 'vue-types'

import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot'

import { makeTruncationRuleSpecification } from '@/utils'
import { AppTypes } from '@/utils/typing'
import { plotify } from '@/utils/plotting'

export default {
  name: 'TruncationMap',

  components: {
    StaticPlot,
  },

  props: {
    value: AppTypes.truncationRule.isRequired,
    expand: VueTypes.bool.def(false),
  },

  asyncComputed: {
    data: {
      async get () {
        return plotify(
          await rms.truncationPolygons(makeTruncationRuleSpecification(this.value, this.$store.getters)),
          this.$store.getters['facies/global/selected']
        )
      },
      shouldUpdate () {
        return this.$store.getters['truncationRules/ready'](this.value.id)
      },
      default () {
        return {
          polygons: [],
          annotations: null,
        }
      },
    },
  },

  methods: {
  },
}
</script>
