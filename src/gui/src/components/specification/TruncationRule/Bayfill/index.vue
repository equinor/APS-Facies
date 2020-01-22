<template>
  <truncation-rule-specification
    :value="value"
    :table="table"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import TruncationRuleSpecification from '../main.vue'
import PolygonTable from './PolygonTable.vue'

import { Bayfill } from '@/utils/domain'
import { Newable } from '@/utils/domain/bases/interfaces'

@Component({
  components: {
    TruncationRuleSpecification,
  },
})
export default class BayfillTruncationRule extends Vue {
  @Prop({ required: true })
  readonly value!: Bayfill

  get table (): Newable<Vue> { return PolygonTable }
}
</script>
