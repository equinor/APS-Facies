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

@Component({
  components: {
    StorableNumericField,
  },
})
export default class RelativeStandardDeviation extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get ranges () {
    return { min: 0, max: 1 }
  }

  propagateError (value: boolean) {
    this.$emit('update:error', value)
  }
}
</script>
