<template>
  <floating-tooltip bottom :disabled="canSimulate" trigger="hover">
    <icon-button
      :disabled="!canSimulate"
      :waiting="waitingForSimulation"
      icon="refresh"
      @click="refresh"
    />
    <template #popper>{{ _explanation }}</template>
  </floating-tooltip>
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
import IconButton from '@/components/selection/IconButton.vue'

import Polygon, {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import TruncationRule from '@/utils/domain/truncationRule/base'

import { TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'
import { usesAllFacies } from '@/store/utils/helpers'

import { displayError } from '@/utils/helpers/storeInteraction'
import { ref, computed } from 'vue'
import { useStore } from '../../../store'

const props = defineProps<{ value: TruncationRule<T, S, P> }>()
const store = useStore()

const waitingForSimulation = ref(false)

const _allFaciesUsed = computed(() =>
  usesAllFacies({ rootGetters: store.getters }, props.value),
)

const _canSimulateAllTrends = computed(
  () =>
    props.value &&
    !props.value.fields.some(
      (field) =>
        field.trend &&
        field.trend.use &&
        TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION.includes(field.trend.type),
    ),
)
const canSimulate = computed(
  () =>
    props.value &&
    props.value.ready &&
    _allFaciesUsed.value &&
    _canSimulateAllTrends.value,
)

const _explanation = computed(() => {
  if (!props.value) return 'No truncation rule has been specified'
  if (!_allFaciesUsed.value) return 'More facies are selected, than are used'
  if (!_canSimulateAllTrends.value) {
    return `Some Gaussian Random Field uses a trend that cannot be simulated in the previewer (${TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION.reduce(
      (prev, curr: string) => `${prev}${prev ? ', ' : ''}'${curr}'`,
      '',
    )})`
  }
  if (!props.value.ready) return props.value.errorMessage
  return undefined
})

async function refresh(): Promise<void> {
  await store.dispatch('facies/normalize')
  waitingForSimulation.value = true
  try {
    await store.dispatch('truncationRules/updateRealization', props.value)
  } catch (e) {
    await displayError(String(e))
  } finally {
    waitingForSimulation.value = false
  }
}
</script>
