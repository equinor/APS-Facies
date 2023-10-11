<template>
  <v-row no-gutters>
    <v-col cols="12">
      <h3>Truncation rule specification overlay facies</h3>
    </v-col>
    <v-col cols="12">
      <overlay-facies-table :value="value" />
    </v-col>
  </v-row>
</template>

<script
  setup
  lang="ts"
  generic="
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
"
>
import OverlayFaciesTable from './table/index.vue'
import Polygon, {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

defineProps<{ value: OverlayTruncationRule<T, S, P> }>()
</script>
