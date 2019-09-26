<template>
  <numeric-field
    v-model="relativeSize"
    label="Relative size of ellipse"
    unit="%"
    fmu-updatable
    enforce-ranges
    :ranges="{min: 0, max: 100}"
    @update:error="e => propagateError(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

import NumericField from '@/components/selection/NumericField.vue'

@Component({
  components: {
    NumericField,
  },
})
export default class RelativeSizeOfEllipse extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get relativeSize () {
    const { value, updatable } = this.value.trend.relativeSize
    return new FmuUpdatableValue({
      value: value * 100,
      updatable
    })
  }
  set relativeSize ({ value, updatable }) {
    this.$store.dispatch('gaussianRandomFields/relativeSize', {
      field: this.value,
      variogramOrTrend: 'trend',
      value: new FmuUpdatableValue({
        value: value / 100,
        updatable,
      })
    })
  }

  propagateError (value: boolean) {
    this.$emit('update:error', value)
  }
}
</script>
