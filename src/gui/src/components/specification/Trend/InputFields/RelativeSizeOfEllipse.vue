<template>
  <storable-numeric-field
    :value="value"
    property-type="relativeSize"
    label="Relative size of ellipse"
    unit="%"
    trend
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'

import StorableNumericField from '@/components/specification/StorableNumericField.vue'

// TODO: Ensure the unit of '%' is correct, and consistent e.g. 100% -> 1
@Component({
  components: {
    StorableNumericField,
  },
})
export default class RelativeSizeOfEllipse extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField
}
</script>
