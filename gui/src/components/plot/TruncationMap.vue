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

import GlobalFacies from '@/utils/domain/facies/global'

import { makeTruncationRuleSpecification } from '@/utils'
import { plotify, PlotSpecification } from '@/utils/plotting'
import { useStore } from '../../store'
import { computed, watch, ref } from 'vue'
import type { TruncationRule } from '@/utils/domain/truncationRule'
import type { Polygon } from '@/utils/domain'
import type { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'

type Props = {
  value: RULE
  expand?: boolean
}
const props = withDefaults(defineProps<Props>(), { expand: false })
const store = useStore()

const data = ref<PlotSpecification>({
  polygons: [],
  annotations: [],
})

const selectedFacies = computed<GlobalFacies[]>(
  () => store.getters['facies/global/selected'],
)

function canUpdate() {
  return store.getters['truncationRules/ready'](props.value)
}

async function getPlotSpecification() {
  return plotify(
    await rms.truncationPolygons(
      makeTruncationRuleSpecification(props.value, store.getters),
    ),
    selectedFacies.value,
  )
}

watch(
  selectedFacies,
  async () => {
    // To detect changes in alias
    if (canUpdate()) {
      data.value = await getPlotSpecification()
    }
  },
  { deep: true },
)
</script>
