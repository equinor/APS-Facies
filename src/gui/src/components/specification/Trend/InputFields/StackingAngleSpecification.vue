<template>
  <div>
    <stacking-angle
      :value="value"
    />
    <item-selection
      v-model="stackingDirection"
      :items="availableStackingDirection"
      :constraints="{ required: true }"
      label="Stacking direction"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StackingAngle from './StackingAngle.vue'
import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'

@Component({
  components: {
    ItemSelection,
    StackingAngle,
  },
})
export default class StackingAngleSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get availableStackingDirection () { return this.$store.state.constants.options.stacking.available }
  get trend () { return this.value.trend }

  get stackingDirection () { return this.trend.stackingDirection }
  set stackingDirection (value) { this.$store.dispatch('gaussianRandomFields/stackingDirection', { field: this.value, value }) }
}
</script>
