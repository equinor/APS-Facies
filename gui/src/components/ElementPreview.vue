<template>
  <v-container fluid>
    <v-row align="center" justify="center">
      <section-title>Preview</section-title>
      <preview-header :value="rule" />
    </v-row>
    <v-row>
      <v-expansion-panels v-model="expanded" accordion multiple>
        <v-expansion-panel
          v-tooltip.bottom="truncationRuleError"
          :disabled="!hasTruncationRule"
        >
          <v-expansion-panel-title>
            <h3>Truncation rule</h3>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-col class="justify-center align-center">
              <truncation-map v-if="!!rule" :value="rule" />
            </v-col>
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel
          v-tooltip.bottom="realizationError"
          :disabled="!hasRealization"
        >
          <v-expansion-panel-title>
            <h3>Realization</h3>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <facies-realization v-if="rule" :value="rule" />
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel>
          <v-expansion-panel-title>
            <h3>Transformed Gaussian Random Fields</h3>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <gaussian-plots :value="fields" />
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel
          v-tooltip.bottom="crossPlotErrors"
          :disabled="!hasEnoughFieldsForCrossPlot"
        >
          <v-expansion-panel-title>
            <h3>Cross plots</h3>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <cross-plots :value="fields" />
          </v-expansion-panel-text>
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
import { GaussianRandomField } from '@/utils/domain'
import { useStore } from '../store'
import { computed, watch } from 'vue'

const store = useStore()

const expanded = computed<number[]>({
  get: () => store.getters['panels/preview'],
  set: (indices: number[]) =>
    store.dispatch('panels/change', { type: 'preview', indices }),
})

const fields = computed<GaussianRandomField[]>(() => {
  return Object.values(store.getters.fields)
})

const rule = computed(() => {
  return store.getters.truncationRule
})

const hasTruncationRule = computed<boolean>(() => {
  return !!rule.value
})

const hasRealization = computed<boolean>(() => {
  return !!(rule.value && rule.value.realization)
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
      await store.dispatch('panels/close', {
        type: 'preview',
        panel: 'crossPlots',
      })
    }
  },
  { deep: true },
)

watch(
  rule,
  async (value) => {
    const type = 'preview'
    if (value) {
      await store.dispatch('panels/open', {
        type,
        panel: 'truncationRuleMap',
      })

      await store.dispatch(`panels/${value.realization ? 'open' : 'close'}`, {
        type,
        panel: 'truncationRuleRealization',
      })
    } else {
      await store.dispatch('panels/close', {
        type,
        panel: ['truncationRuleMap', 'truncationRuleRealization'],
      })
    }
  },
  { deep: true },
)
</script>
