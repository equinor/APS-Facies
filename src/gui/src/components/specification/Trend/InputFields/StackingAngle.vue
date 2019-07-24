<template>
  <storable-numeric-field
    :value="value"
    property-type="angle"
    sub-property-type="stacking"
    value-type="stacking"
    label="Stacking angle"
    unit="°"
    trend
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
export default class StackingAngle extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField
}
</script>
