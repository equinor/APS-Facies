<template>
  <h3>Alpha selection</h3>
  <alpha-fields :value="props.value" :min-fields="minFields" />
  <h3>Truncation rule specification background facies</h3>
  <v-row no-gutters>
    <v-col>
      <v-row no-gutters>
        <v-col>
          <component :is="props.table" :value="value" />
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script
    setup
    lang="ts"
    generic="T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRule<T, S, P>
">
import AlphaFields from '@/components/specification/TruncationRule/AlphaFields.vue'

import type { TruncationRule } from '@/utils/domain/truncationRule'
import { computed } from 'vue'
import { type Component } from 'vue'
import type { Polygon, PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'

type Props = {
  value: RULE
  table: Component
}
const props = defineProps<Props>()

const minFields = computed(() => (props.value.type === 'bayfill' ? 3 : 2))
</script>
