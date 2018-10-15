<template>
  <div>
    <stacking-angle
      :grf-id="grfId"
    />
    <v-select
      :items="availableStackingDirection"
      v-model="stackingDirection"
      label="Stacking direction"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'
import VueTypes from 'vue-types'
import StackingAngle from './StackingAngle'

export default {
  components: {
    StackingAngle,
  },

  props: {
    grfId: VueTypes.string.isRequired,
  },

  computed: {
    ...mapState({
      availableStackingDirection: state => state.constants.options.stacking.available,
    }),
    trend () { return this.$store.state.gaussianRandomFields.fields[this.grfId].trend },
    stackingDirection: {
      get: function () { return this.trend.stackingDirection },
      set: function (value) { this.$store.dispatch('gaussianRandomFields/stackingDirection', { grfId: this.grfId, value }) }
    },
  },
}
</script>
