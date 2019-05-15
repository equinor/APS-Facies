<template>
  <v-container>
    <cubic-truncation-rule-specification
      :value="value"
    />
    <cubic-facies-selection
      v-if="value.root"
      :value="value"
    />
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import CubicTruncationRuleSpecification from '@/components/specification/TruncationRule/Cubic/table/specification/index.vue'
import CubicFaciesSelection from '@/components/specification/TruncationRule/Cubic/table/table.vue'

import { Cubic } from '@/utils/domain'

@Component({
  components: {
    CubicTruncationRuleSpecification,
    CubicFaciesSelection,
  },
})
export default class CubicTable extends Vue {
  @Prop({ required: true })
  readonly value!: Cubic
}
</script>
