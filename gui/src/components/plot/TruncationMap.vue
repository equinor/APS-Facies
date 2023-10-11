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

<script setup lang="ts">
import rms from '@/api/rms'

import StaticPlot from '@/components/plot/StaticPlot.vue'

import { TruncationRule } from '@/utils/domain'
import GlobalFacies from '@/utils/domain/facies/global'

import { makeTruncationRuleSpecification } from '@/utils'
import { plotify, PlotSpecification } from '@/utils/plotting'
import { useStore } from '../../store'
import { computed, watch, ref } from 'vue'

type Props = {
  value: TruncationRule
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
