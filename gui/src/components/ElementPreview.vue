<template>
  <v-container fluid>
    <v-row align="center" justify="center">
      <section-title>Preview</section-title>
      <preview-header v-if="rule" :value="rule" />
    </v-row>
    <v-row>
      <v-expansion-panels v-model="expanded" variant="accordion" multiple>
        <v-expansion-panel
          v-tooltip.bottom="truncationRuleError"
          :disabled="!hasTruncationRule"
          value="truncationRuleMap"
          elevation="0"
        >
          <template #title>
            <h3>Truncation rule</h3>
          </template>
          <template #text>
            <v-col class="justify-center align-center">
              <truncation-map v-if="!!rule" :value="rule" />
            </v-col>
          </template>
        </v-expansion-panel>
        <v-expansion-panel
          v-tooltip.bottom="realizationError"
          :disabled="!hasRealization"
          value="truncationRuleRealization"
          elevation="0"
        >
          <template #title>
            <h3>Realization</h3>
          </template>
          <template #text>
            <facies-realization v-if="rule" :value="rule" />
          </template>
        </v-expansion-panel>
        <v-expansion-panel
          value="gaussianRandomFields"
          elevation="0"
        >
          <template #title>
            <h3>Transformed Gaussian Random Fields</h3>
          </template>
          <template #text>
            <gaussian-plots :value="fields" />
          </template>
        </v-expansion-panel>
        <v-expansion-panel
          v-tooltip.bottom="crossPlotErrors"
          :disabled="!hasEnoughFieldsForCrossPlot"
          value="crossPlots"
          elevation="0"
        >
          <template #title>
            <h3>Cross plots</h3>
          </template>
          <template #text>
            <cross-plots :value="fields" />
          </template>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'
import TruncationMap from '@/components/plot/TruncationMap.vue'
import FaciesRealization from '@/components/plot/FaciesRealization.vue'
import GaussianPlots from '@/components/plot/GaussianPlot/multiple.vue'
import PreviewHeader from '@/components/visualization/preview/header.vue'
import CrossPlots from '@/components/plot/CrossPlot/multiple.vue'
import type { GaussianRandomField } from '@/utils/domain'
import { computed, watch } from 'vue'
import { usePanelStore } from '@/stores/panels'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useTruncationRuleStore } from '@/stores/truncation-rules'

const fieldStore = useGaussianRandomFieldStore()
const ruleStore = useTruncationRuleStore()

const panelStore = usePanelStore()

const expanded = computed({
  get: () => panelStore.getOpen('preview'),
  set: (panelNames: string[]) => {
    panelStore.setOpen('preview', panelNames)
  },
})

const fields = computed<GaussianRandomField[]>(() => {
  return fieldStore.selected as GaussianRandomField[]
})

const rule = computed(() => {
  return ruleStore.current
})

const hasTruncationRule = computed<boolean>(() => {
  return !!rule.value
})

const hasRealization = computed<boolean>(() => {
  return !!(rule.value && rule.value?.realization)
})

const hasEnoughFieldsForCrossPlot = computed<boolean>(() => {
  return fields.value.length >= 2
})

const truncationRuleError = computed<string | undefined>(() => {
  return !hasTruncationRule.value
    ? 'No truncation rule has been specified'
    : undefined
})

const realizationError = computed<string | undefined>(() => {
  return truncationRuleError.value || !hasRealization.value
    ? 'The realization has not been simulated'
    : undefined
})

const crossPlotErrors = computed<string | undefined>(() => {
  return !hasEnoughFieldsForCrossPlot.value
    ? 'There must be at least two Gaussian Fields before their cross variance plot can be made'
    : undefined
})

watch(
  fields,
  async (value: GaussianRandomField[]) => {
    if (value.length < 2) {
      panelStore.close('preview', 'crossPlots')
    }
  },
  { deep: true },
)

watch(
  rule,
  (value) => {
    if (value) {
      panelStore.open('preview', 'truncationRuleMap')
      const realized = !!value.realization
      panelStore.set('preview', 'truncationRuleRealization', realized)
    } else {
      panelStore.close('preview', 'truncationRuleMap')
      panelStore.close('preview', 'truncationRuleRealization')
    }
  },
  { deep: true },
)
</script>
