<template>
  <static-plot
    :data-definition="polygons"
    svg
  />
</template>

<script>
import VueTypes from 'vue-types'

import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot'

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

const allSet = (items, prop) => {
  return Object.values(items).every(item => !!item[`${prop}`])
}

export default {
  name: 'TruncationMap',

  components: {
    StaticPlot,
  },

  props: {
    truncationRuleId: VueTypes.string.isRequired,
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
        return rms.truncationPolygons({
          type: 'bayfill',
          globalFaciesTable: this.$store.getters['facies/selected']
            .map(facies => {
              return {
                code: facies.code,
                name: facies.name,
                probability: facies.previewProbability,
                inZone: true,
                inRule: rule.polygons.findIndex(polygon => polygon.facies === facies.id),
              }
            }),
          gaussianRandomFields: Object.values(this.$store.getters.fields)
            .map(field => {
              return {
                name: field.name,
                inZone: true,
                inRule: rule.fields.findIndex(item => item.field === field.id),
              }
            }),
          values: Object.values(rule.settings),
          constantParameters: !this.$store.getters.faciesTable.some(facies => !!facies.probabilityCube),
        }).then(polygons => plotify(polygons, this.$store.getters.faciesTable))
      },
      shouldUpdate () {
        return !!this.rule &&
          allSet(this.rule.fields, 'field') &&
          allSet(this.rule.polygons, 'facies')
      },
      default () { return [] },
    },
  },

  methods: {
  },
}
</script>
