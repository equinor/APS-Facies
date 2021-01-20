<template>
  <div>
    <stacking-angle
      :value="value"
      @update:error="e => update('angle', e)"
    />
    <item-selection
      v-model="stackingDirection"
      :items="availableStackingDirection"
      :constraints="{ required: true }"
      label="Stacking direction"
      @update:error="e => update('type', e)"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import Trend, { StackingDirectionType } from '@/utils/domain/gaussianRandomField/trend'

import StackingAngle from './StackingAngle.vue'
import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'

interface Invalid {
  angle: boolean
  type: boolean
}

@Component({
  components: {
    ItemSelection,
    StackingAngle,
  },
})
export default class StackingAngleSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  invalid: Invalid = {
    angle: false,
    type: false,
  }

  get availableStackingDirection (): StackingDirectionType[] { return this.$store.state.constants.options.stacking.available }
  get trend (): Trend { return this.value.trend }

  get stackingDirection (): StackingDirectionType { return this.trend.stackingDirection }
  set stackingDirection (value) { this.$store.dispatch('gaussianRandomFields/stackingDirection', { field: this.value, value }) }

  @Watch('invalid', { deep: true })
  propagateError ({ angle, type }: Invalid): void {
    this.$emit('update:error', angle || type)
  }

  update (type: string, value: boolean): void {
    Vue.set(this.invalid, type, value)
  }
}
</script>
