<template>
  <base-polygon-order
    :can-increase="canIncrease"
    :can-decrease="canDecrease"
    :can-remove="canRemove"
    :can-add="canAdd"
    @input="direction => changeOrder(direction)"
    @add="addPolygon"
    @delete="deletePolygon"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import {
  OverlayPolygon,
} from '@/utils/domain'

import BasePolygonOrder from '@/components/specification/PolygonOrder.vue'

@Component({
  components: {
    BasePolygonOrder,
  },
})
export default class PolygonOrder<T extends Polygon, S extends PolygonSerialization> extends Vue {
  @Prop({ required: true })
  readonly value!: T

  @Prop({ required: true })
  readonly rule!: TruncationRule<T, S>

  @Prop({ default: false, type: Boolean })
  readonly overlay: boolean

  get max () {
    return (this.rule.polygons as Polygon[])
      .filter(polygon => polygon.overlay === this.overlay)
      .map(polygon => polygon.order)
      .reduce((max, order) => order > max ? order : max, 0)
  }
  get min (): number {
    return Math.min(
      ...this.rule.polygons
        .filter(polygon => polygon.overlay === this.overlay)
        .map(({ order }) => order)
    )
  }
  get canIncrease () {
    return this.value.order < this.max
  }
  get canDecrease () {
    return this.value.order > this.min
  }
  get canRemove (): boolean {
    return true
  }
  get canAdd (): boolean {
    return true
  }

  addPolygon () {
    return this.$store.dispatch('truncationRules/addPolygon', {
      rule: this.rule,
      order: this.value.order + 1,
      overlay: this.value.overlay,
      group: this.value instanceof OverlayPolygon ? this.value.group : null,
    })
  }
  deletePolygon () {
    return this.$store.dispatch('truncationRules/removePolygon', { rule: this.rule, polygon: this.value })
  }
  changeOrder (direction: number) {
    return this.$store.dispatch('truncationRules/changeOrder', { rule: this.rule, polygon: this.value, direction })
  }
}
</script>
