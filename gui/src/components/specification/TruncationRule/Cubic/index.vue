<template>
  <truncation-rule-specification
    :value="value"
    :table="table"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import TruncationRuleSpecification from '../main.vue'
import PolygonTable from './table/index.vue'

import { Cubic } from '@/utils/domain'
import { Newable } from '@/utils/domain/bases/interfaces'

@Component({
  components: {
    TruncationRuleSpecification,
  },
})
export default class CubicTruncationRule extends Vue {
  @Prop({ required: true })
  readonly value!: Cubic

  get table (): Newable<Vue> { return PolygonTable }
}
</script>
