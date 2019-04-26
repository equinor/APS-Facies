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

import {
  Polygon,
  TruncationRule,
} from '@/utils/domain'

import BasePolygonOrder from '@/components/specification/PolygonOrder.vue'

@Component({
  components: {
    BasePolygonOrder,
  },
})
export default class PolygonOrder extends Vue {
  @Prop({ required: true })
  readonly value!: { /* TODO: Define the correct type */
    order: number
    overlay?: boolean
    [_: string]: any
  }
  @Prop({ default: false })
  readonly overlay: boolean

  get rule (): TruncationRule<Polygon> { return this.$store.getters['truncationRule'] }
  get max () {
    return this.rule.polygons
      .filter(polygon => polygon.overlay === this.overlay)
      .map(polygon => polygon.order)
      .reduce((max, order) => order > max ? order : max, 0)
  }
  get min (): number {
    return 0
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
      group: this.value.overlay ? this.value.group : null,
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
