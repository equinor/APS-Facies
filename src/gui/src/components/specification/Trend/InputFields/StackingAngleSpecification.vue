<template>
  <div>
    <stacking-angle
      :grf-id="grfId"
    />
    <item-selection
      v-model="stackingDirection"
      :items="availableStackingDirection"
      :constraints="{ required: true }"
      label="Stacking direction"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { AppTypes } from '@/utils/typing'
import StackingAngle from './StackingAngle'
import ItemSelection from '@/components/selection/dropdown/ItemSelection'

export default {
  components: {
    ItemSelection,
    StackingAngle,
  },

  props: {
    grfId: AppTypes.id.isRequired,
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
