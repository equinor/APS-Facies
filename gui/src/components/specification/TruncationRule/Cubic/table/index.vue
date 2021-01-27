<template>
  <v-row
    justify="center"
    align="center"
    no-gutters
  >
    <v-col cols="12">
      <cubic-truncation-rule-specification
        :value="value"
      />
    </v-col>
    <v-col cols="12">
      <cubic-facies-selection
        v-if="value.root"
        :value="value"
      />
    </v-col>
  </v-row>
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
