<template>
  <v-row class="ma-0 pa-0 shrink" align="center" justify="center">
    <static-plot
      :data-definition="data.polygons"
      :annotations="data.annotations"
      :expand="expand"
      svg
    />
  </v-row>
</template>

<script
  setup
  lang="ts"
  generic="T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRule<T, S, P>
"
>
import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { makeTruncationRuleSpecification } from '@/utils'
import { plotify } from '@/utils/plotting'
import type { PlotSpecification } from '@/utils/plotting'
import { ref, watch } from 'vue'
import type { TruncationRule } from '@/utils/domain/truncationRule'
import type { Polygon } from '@/utils/domain'
import type { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import { useFaciesGlobalStore } from '@/stores/facies/global'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

type Props = {
  value: RULE
  expand?: boolean
}
const props = withDefaults(defineProps<Props>(), { expand: false })
const faciesGlobalStore = useFaciesGlobalStore()
const ruleStore = useTruncationRuleStore()

const data = ref<PlotSpecification>({
  polygons: [],
  annotations: [],
})

watch(
  [
    () => props.value,
    // Vue struggles with changes in class properties
    () => props.value.facies,
    () => props.value.polygons.map(polygon => polygon.facies?.previewProbability),
  ],
  async () => {
    if (ruleStore.ready(props.value)) {

      data.value = plotify(
        await rms.truncationPolygons(makeTruncationRuleSpecification(props.value)),
        faciesGlobalStore.selected,
      )}
  }, {
    deep: true,
    immediate: true,
  })

</script>
