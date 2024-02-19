<template>
  <floating-tooltip
    placement="bottom"
    :triggers="_explanation ? ['hover'] : []"
    :disabled="!!_explanation"
    v-tooltip="_explanation"
  >
    <icon-button
      :disabled="!!_explanation"
      :waiting="waitingForSimulation"
      icon="refresh"
      @click="refresh"
    />
  </floating-tooltip>
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
import IconButton from '@/components/selection/IconButton.vue'

import type {
  Polygon,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type TruncationRule from '@/utils/domain/truncationRule/base'

import { TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'

import { displayError } from '@/utils/helpers/storeInteraction'
import { ref, computed, watch } from 'vue'
import { usesAllFacies } from '@/stores/truncation-rules/utils'
import { useFaciesStore } from '@/stores/facies'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

const props = defineProps<{ value: RULE }>()
const faciesStore = useFaciesStore()
const ruleStore = useTruncationRuleStore()

const waitingForSimulation = ref(false)

const _explanation = ref<string | undefined>(undefined)

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

watch([
  props.value,
], () => {
  _explanation.value = (() => {
    // Ensure `ready`, and `errorMessage` are executed every time there is a change in props.value
    // otherwise vue / pinia seem to have problems detecting that the result will change
    if (!props.value) return 'No truncation rule has been specified'
    if (!usesAllFacies(props.value)) return 'More facies are selected, than are used'
    if (!_canSimulateAllTrends.value) {
      return `Some Gaussian Random Field uses a trend that cannot be simulated in the previewer (${TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION.reduce(
        (prev, curr: string) => `${prev}${prev ? ', ' : ''}'${curr}'`,
        '',
      )})`
    }
    if (!props.value.ready) return props.value.errorMessage
    return undefined
  })()
})

async function refresh(): Promise<void> {
  await faciesStore.normalize()
  waitingForSimulation.value = true
  try {
    await ruleStore.updateRealization(props.value)
  } catch (e) {
    displayError(String(e))
  } finally {
    waitingForSimulation.value = false
  }
}
</script>
