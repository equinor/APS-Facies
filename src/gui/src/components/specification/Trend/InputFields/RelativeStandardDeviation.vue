<template>
  <storable-numeric-field
    :grf-id="grfId"
    :arrow-step="0.01"
    :ranges="ranges"
    property-type="relativeStdDev"
    label="Relative std. dev."
    trend
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import StorableNumericField from '@/components/specification/StorableNumericField.vue'
import { ID } from '@/utils/domain/types'

@Component({
  components: {
    StorableNumericField,
  },
})
export default class RelativeStandardDeviation extends Vue {
  @Prop({ required: true })
  readonly grfId!: ID

  get ranges () {
    return { min: 0, max: 1 }
  }
}
</script>
