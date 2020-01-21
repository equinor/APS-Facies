<template>
  <storable-numeric-field
    :value="value"
    label="Migration angle"
    property-type="angle"
    sub-property-type="migration"
    value-type="migration"
    unit="°"
    trend
    @update:error="e => propagateError(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

@Component({
  components: {
    StorableNumericField,
  },
})
export default class MigrationAngle extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  propagateError (value: boolean): void {
    this.$emit('update:error', value)
  }
}
</script>
