<template>
  <numeric-field
    :value="value"
    :arrow-step="0.01"
    :ranges="ranges"
    :fmu-updatable="fmuUpdatable"
    :disabled="disabled"
    :label="label"
    optional
    enforce-ranges
    @input="e => propagate(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'

import { Optional } from '@/utils/typing'
import NumericField from '@/components/selection/NumericField.vue'

@Component({
  components: {
    NumericField,
  },
})
export default class FractionField extends Vue {
  @Prop({ required: true })
  readonly value!: Optional<number> | FmuUpdatable

  @Prop({ required: false, default: false, type: Boolean })
  readonly fmuUpdatable!: boolean

  @Prop({ required: false, default: false, type: Boolean })
  readonly disabled!: boolean

  @Prop({ required: false, default: '' })
  readonly label!: string

  get ranges () {
    return {
      min: 0,
      max: 1,
    }
  }

  propagate (value: any) {
    this.$emit('input', value)
  }
}
</script>
