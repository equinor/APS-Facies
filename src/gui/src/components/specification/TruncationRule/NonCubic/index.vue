<template>
  <truncation-rule-specification
    :value="value"
    :table="table"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import TruncationRuleSpecification from '../main.vue'
import PolygonTable from './table.vue'

import { NonCubic } from '@/utils/domain'

@Component({
  components: {
    TruncationRuleSpecification,
  },
})
export default class NonCubicTruncationRule extends Vue {
  @Prop({ required: true })
  readonly value!: NonCubic

  get table () { return PolygonTable }
}
</script>
