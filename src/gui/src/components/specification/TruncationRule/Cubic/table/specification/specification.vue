<template>
  <static-plot
    :data-definition="data.polygons"
    :annotations="data.annotations"
    :max-height="maxSize.height"
    :max-width="maxSize.width"
    expand
    svg
    @click.native="clicked"
  />
</template>

<script>
import VueTypes from 'vue-types'

import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { getId, makeSimplifiedTruncationRuleSpecification } from '@/utils'
import { AppTypes } from '@/utils/typing'
import { plotify } from '@/utils/plotting'

export default {
  name: 'CubicTopologySpecification',

  components: {
    StaticPlot,
  },

  props: {
    value: VueTypes.arrayOf(AppTypes.polygon.cubic).isRequired,
    rule: AppTypes.truncationRule.isRequired,
  },

  data () {
    return {
      polygons: [],
    }
  },

  computed: {
    maxSize () {
      return {
        width: 400,
        height: 400,
      }
    },
    data () {
      return plotify(
        this.polygons
          .concat() /* Necessary to copy the array, as to not sort it in-place */
          .sort((a, b) => {
            const selected = this.value.map(getId)
            if (!selected.includes(a.name) && !selected.includes(b.name)) return 0
            return selected.includes(a.name) - selected.includes(b.name)
          }),
        this.rule.backgroundPolygons.map(polygon => {
          return {
            name: polygon.id,
            color: this.has(polygon)
              ? this.$vuetify.theme.primary
              : '#000',
            alias: polygon.level.filter(lvl => lvl !== 0).join('.'),
          }
        }),
        '#fff',
      )
    },
    boundingBoxes () {
      return this.polygons.map(({ name, polygon }) => {
        return {
          name,
          boundingBox: polygon.reduce((box, [x, y]) => {
            box.minX = Math.min(box.minX, x)
            box.maxX = Math.max(box.maxX, x)
            box.minY = Math.min(box.minY, 1 - y)
            box.maxY = Math.max(box.maxY, 1 - y)
            return box
          }, {
            minX: Number.POSITIVE_INFINITY,
            maxX: Number.NEGATIVE_INFINITY,
            minY: Number.POSITIVE_INFINITY,
            maxY: Number.NEGATIVE_INFINITY,
          })
        }
      })
    }
  },

  watch: {
    'rule': {
      immediate: true,
      deep: true,
      async handler () {
        let polygons = null
        try {
          polygons = await rms.truncationPolygons(makeSimplifiedTruncationRuleSpecification(this.rule))
        } catch (e) {
          // Ignore, as a cubic truncation rule may be inconsistent during an (vuex) action
        }
        if (polygons) this.polygons = polygons
      },
    },
  },

  methods: {
    clicked (e) {
      const { x, y } = this.relativeClickPosition(e)
      const { name } = this.boundingBoxes.find(({ boundingBox }) => (
        boundingBox.minX <= x && x <= boundingBox.maxX
        && boundingBox.minY <= y && y <= boundingBox.maxY
      ))
      if (this.has(name)) {
        this.$emit('input', this.value.filter(item => getId(item) !== name))
      } else {
        this.$emit('input', [...this.value, this.rule.polygons.find(polygon => getId(polygon) === name)])
      }
    },
    relativeClickPosition (e) {
      const { top, bottom, left, right } = this.$el.getElementsByClassName('svg-container')[0].getBoundingClientRect()
      const getMax = (direction) => Math.max(...this.boundingBoxes.map(({ boundingBox }) => boundingBox[`max${direction.toUpperCase()}`]))
      return {
        x: Math.min((e.clientX - left) / (right - left), getMax('x')),
        y: Math.min((e.clientY - top) / (bottom - top), getMax('y')),
      }
    },
    has (item) {
      return this.value.map(getId).includes(getId(item))
    },
  },
}
</script>
