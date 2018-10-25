<template>
  <static-plot
    :data-definition="polygons"
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

const svgPoint = (point, width = 1, height = 1) => {
  return `${point[0] * width},${point[1] * height}`
}

const polygon2svg = (polygon, width = 1, height = 1) => {
  return polygon.reduce((path, point) => path.concat(` L ${svgPoint(point, width, height)}`), `M ${svgPoint(polygon[0], width, height)}`).concat(' Z')
}

const plotify = (polygons, faciesTable) => {
  return polygons
    .map(item => {
      const color = faciesTable.find(facies => facies.name === item.name).color
      return {
        type: 'path',
        path: polygon2svg(item.polygon),
        fillcolor: color,
        name: item.name,
        line: {
          color: color,
        },
      }
    })
}

export default {
  name: 'TruncationMap',

  components: {
    StaticPlot,
  },

  props: {
    truncationRuleId: AppTypes.id.isRequired,
    expand: VueTypes.bool.def(false),
  },

  computed: {
    rule () {
      return this.truncationRuleId
        ? this.$store.state.truncationRules.rules[this.truncationRuleId]
        : null
    }
  },

  asyncComputed: {
    polygons: {
      get () {
        const rule = this.rule
        return rms.truncationPolygons(makeTruncationRuleSpecification(rule, this.$store.getters))
          .then(polygons => plotify(polygons, this.$store.getters.faciesTable))
      },
      shouldUpdate () {
        return this.$store.getters['truncationRules/ready'](this.truncationRuleId)
      },
      default () { return [] },
    },
  },

  methods: {
  },
}
</script>
