<template>
  <storable-numeric-field
    :value="value"
    :property-type="propertyType"
    :arrow-step="0.01"
    value-type="power"
    label="Power"
    unit=""
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
export default class PowerSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get propertyType () { return 'power' }
}
</script>
