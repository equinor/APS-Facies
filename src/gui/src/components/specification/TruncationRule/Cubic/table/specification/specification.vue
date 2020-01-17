<template>
  <static-plot
    :data-definition="__data.polygons"
    :annotations="__data.annotations"
    :width="300"
    :height="300"
    :max-height="maxSize.height"
    :max-width="maxSize.width"
    expand
    svg
    @click.native="clicked"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { ID } from '@/utils/domain/types'
import { Cubic } from '@/utils/domain'
import CubicPolygon from '@/utils/domain/polygon/cubic'
import { PolygonDescription } from '@/api/types'

import { getId, makeSimplifiedTruncationRuleSpecification } from '@/utils'
import { plotify, PlotSpecification } from '@/utils/plotting'

interface BoundingBox {
  minX: number
  minY: number
  maxX: number
  maxY: number
}

@Component({
  components: {
    StaticPlot,
  },
})
export default class CubicTopologySpecification extends Vue {
  @Prop({ required: true })
  readonly value!: CubicPolygon[]

  @Prop({ required: true })
  readonly rule!: Cubic

  polygons: PolygonDescription[] = []

  get maxSize (): { width: number, height: number } {
    return {
      width: 400,
      height: 400,
    }
  }

  get __data (): PlotSpecification {
    return plotify(
      this.polygons
        .concat() /* Necessary to copy the array, as to not sort it in-place */
        .sort((a, b) => {
          const selected = this.value.map(getId)
          if (!selected.includes(a.name) && !selected.includes(b.name)) return 0
          return Number(selected.includes(a.name)) - Number(selected.includes(b.name))
        }),
      this.rule.backgroundPolygons.map(polygon => {
        return {
          name: polygon.id,
          color: this.has(polygon)
            ? (this.$vuetify.theme.themes.light.primary as string)
            : '#000',
          alias: polygon.level.filter(lvl => lvl !== 0).join('.'),
        }
      }),
      '#fff',
    )
  }

  get boundingBoxes (): { name: string, boundingBox: BoundingBox }[] {
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

  @Watch('rule', { deep: true, immediate: true })
  async handler (): Promise<void> {
    let polygons = null
    try {
      polygons = await rms.truncationPolygons(makeSimplifiedTruncationRuleSpecification(this.rule))
    } catch (e) {
      // Ignore, as a cubic truncation rule may be inconsistent during an (vuex) action
    }
    if (polygons) this.polygons = polygons
  }

  clicked (e: MouseEvent): void {
    const { x, y } = this.relativeClickPosition(e)
    const { name } = this.boundingBoxes.find(({ boundingBox }) => (
      boundingBox.minX <= x && x <= boundingBox.maxX
      && boundingBox.minY <= y && y <= boundingBox.maxY
    )) || { name: undefined }
    if (name === undefined) {
      this.$emit('input', this.value)
    } else if (this.has(name)) {
      this.$emit('input', this.value.filter(item => getId(item) !== name))
    } else {
      this.$emit('input', [...this.value, this.rule.polygons.find(polygon => getId(polygon) === name)])
    }
  }

  relativeClickPosition (e: MouseEvent): { x: number, y: number } {
    const { top, bottom, left, right } = this.$el.getElementsByClassName('svg-container')[0].getBoundingClientRect()
    const getMax = (direction: string) => Math.max(...this.boundingBoxes.map(({ boundingBox }) => boundingBox[`max${direction.toUpperCase()}`]))
    return {
      x: Math.min((e.clientX - left) / (right - left), getMax('x')),
      y: Math.min((e.clientY - top) / (bottom - top), getMax('y')),
    }
  }

  has (item: CubicPolygon | ID | undefined): boolean {
    return this.value.map(getId).includes(getId(item))
  }
}
</script>
