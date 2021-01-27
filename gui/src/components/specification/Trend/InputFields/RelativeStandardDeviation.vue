<template>
  <storable-numeric-field
    :value="value"
    :arrow-step="0.01"
    :ranges="ranges"
    property-type="relativeStdDev"
    label="Relative std. dev."
    trend
    @update:error="e => propagateError(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import StorableNumericField from '@/components/specification/StorableNumericField.vue'
import { GaussianRandomField } from '@/utils/domain'
import { MinMax } from '@/api/types'

@Component({
  components: {
    StorableNumericField,
  },
})
export default class RelativeStandardDeviation extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get ranges (): MinMax {
    return { min: 0, max: 1 }
  }

  propagateError (value: boolean): void {
    this.$emit('update:error', value)
  }
}
</script>
