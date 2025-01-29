<template>
  <v-row no-gutters>
    <v-col cols="12">
      <h3>Truncation rule specification overlay facies</h3>
    </v-col>
    <v-col cols="12">
      <overlay-facies-table :value="props.value" />
    </v-col>
  </v-row>
</template>

<script
  setup
  lang="ts"
  generic="
    T extends OverlayPolygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends
      | OverlayTruncationRule<T, S, P>
      | InstantiatedOverlayTruncationRule
  "
>
import OverlayFaciesTable from './table/index.vue'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type {
  InstantiatedOverlayTruncationRule,
  OverlayPolygon,
} from '@/utils/domain'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

const props = defineProps<{ value: RULE }>()
</script>
