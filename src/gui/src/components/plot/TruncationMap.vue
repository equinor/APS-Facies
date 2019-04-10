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
import hexRgb from 'hex-rgb'
import colors from 'vuetify/es5/util/colors'

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

function average (arr) {
  return arr.reduce((sum, e) => sum + e, 0) / arr.length
}

function centerOfPolygon (polygon) {
  const points = polygon
    .reduce((obj, [x, y]) => {
      obj.x.push(x)
      obj.y.push(y)
      return obj
    }, {
      x: [],
      y: [],
    })
  return {
    x: average(points.x),
    y: average(points.y),
  }
}

function luminance ({ red, green, blue }) {
  /* Borrowed from https://stackoverflow.com/questions/9733288/how-to-programmatically-calculate-the-contrast-ratio-between-two-colors
  * */
  const [x, y, z] = [red, green, blue].map(v => {
    v /= 255
    return v <= 0.03928
      ? v / 12.92
      : Math.pow((v + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * x + 0.7152 * y + 0.0722 * z
}

function contrast (color, other) {
  return (
    (luminance(hexRgb(color)) + 0.05)
    / (luminance(hexRgb(other)) + 0.05)
  )
}

function getTextColor (backgroundColor) {
  const textColor = colors.grey.darken3
  return contrast(backgroundColor, textColor) <= 4.5
    ? colors.grey.lighten4
    : textColor
}

const plotify = (polygons, faciesTable) => {
  return polygons.reduce((obj, { name, polygon }) => {
    const facies = faciesTable.find(facies => facies.name === name)
    const color = facies.color

    // Add SVG polygon
    obj.polygons.push({
      type: 'path',
      path: polygon2svg(polygon),
      fillcolor: color,
      name,
      line: {
        color,
      },
    })

    // Add alias to polygons
    const { x, y } = centerOfPolygon(polygon)
    obj.annotations.push({
      x,
      y,
      xref: 'x',
      yref: 'y',
      text: facies.alias,
      font: {
        color: getTextColor(color)
      },
      showarrow: false,
    })

    return obj
  }, {
    polygons: [],
    annotations: [],
  })
}

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
