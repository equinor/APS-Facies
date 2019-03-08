<template>
  <polygon-order
    :can-increase="canIncrease"
    :can-decrease="canDecrease"
    :can-remove="canRemove"
    :can-add="canAdd"
    @input="direction => changeOrder(direction)"
    @add="addPolygon"
    @delete="deletePolygon"
  />
</template>

<script>
import VueTypes from 'vue-types'
import { mapGetters } from 'vuex'

import PolygonOrder from '@/components/specification/PolygonOrder'

export default {
  components: {
    PolygonOrder,
  },

  props: {
    value: VueTypes.shape({
      order: VueTypes.integer.isRequired,
      overlay: VueTypes.bool,
    }).loose.isRequired,
    overlay: VueTypes.bool,
  },

  computed: {
    ...mapGetters({
      rule: 'truncationRule',
    }),
    max () {
      return this.rule.polygons
        .filter(polygon => polygon.overlay === this.overlay)
        .map(polygon => polygon.order)
        .reduce((max, order) => order > max ? order : max, 0)
    },
    min () {
      return 0
    },
    canIncrease () {
      return this.value.order < this.max
    },
    canDecrease () {
      return this.value.order > this.min
    },
    canRemove () {
      return true
    },
    canAdd () {
      return true
    },
  },

  methods: {
    addPolygon () {
      return this.$store.dispatch('truncationRules/addPolygon', { rule: this.rule, ...this.value })
    },
    deletePolygon () {
      return this.$store.dispatch('truncationRules/removePolygon', { rule: this.rule, polygon: this.value })
    },
    changeOrder (direction) {
      return this.$store.dispatch('truncationRules/changeOrder', { rule: this.rule, polygon: this.value, direction })
    },
  },
}
</script>
