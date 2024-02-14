<template>
  <v-container class="align justify center" fluid>
    <v-row>
      <v-expansion-panels v-model="expanded" variant="accordion" multiple>
        <section-title>{{ title }}</section-title>
        <v-expansion-panel
          value="faciesProbability"
          v-tooltip.bottom-start="!hasFacies && 'No Facies has been selected'"
          :disabled="!hasFacies"
          elevation="0"
        >
          <v-expansion-panel-title>
            <section-title>Probabilities for Facies</section-title>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <facies-probability-cube />
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel
          value="truncationRule"
          v-tooltip.bottom="
            !hasEnoughFacies && 'Too few Facies has been selected'
          "
          :disabled="!hasEnoughFacies"
          elevation="0"
        >
          <v-expansion-panel-title>
            <section-title>Truncation Rule</section-title>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <truncation-rule />
          </v-expansion-panel-text>
        </v-expansion-panel>
        <gaussian-random-fields />
      </v-expansion-panels>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple.vue'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube/index.vue'
import TruncationRule from '@/components/specification/TruncationRule/index.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import { isEmpty } from '@/utils'

import { Facies } from '@/utils/domain'
import { useStore } from '../store'
import { computed, watch } from 'vue'

type Option = 'number' | 'name'

const store = useStore()
const options = computed(() => {
  const showNameOrNumber = store.state.options.showNameOrNumber
  return {
    zone: showNameOrNumber.zone.value as Option,
    region: showNameOrNumber.region.value as Option,
  }
})

const expanded = computed<number[]>({
  get: () => store.getters['panels/settings'],
  set: (indices: number[]) =>
    store.dispatch('panels/change', { type: 'settings', indices }),
})

const title = computed<string>(() =>
  `Settings for ${zoneName.value}`.concat(
    useRegions.value ? ` / ${regionName.value}` : '',
  ),
)

const useRegions = computed<boolean>(() => store.state.regions.use)

// TODO: Combine common logic in zone/regionName
const zoneName = computed<string>(() => {
  const current = store.getters.zone
  return isEmpty(current)
    ? ''
    : options.value.zone === 'name'
    ? current.name
    : `Zone ${current.code}`
})

const regionName = computed<string>(() => {
  const current = store.getters.region
  return isEmpty(current)
    ? ''
    : options.value.region === 'name'
    ? current.name
    : `Region ${current.code}`
})

const _facies = computed<Facies[]>(() => store.getters['facies/selected'])

const hasFacies = computed<boolean>(() => _facies.value.length > 0)

const hasEnoughFacies = computed<boolean>(
  () => _facies.value.length >= 2,
) /* TODO: Use a constant */

watch(
  _facies,
  async () => {
    await store.dispatch(`panels/${hasEnoughFacies.value ? 'open' : 'close'}`, {
      type: 'settings',
      panel: 'truncationRule',
    })
    if (!hasFacies.value) {
      await store.dispatch('panels/close', {
        type: 'settings',
        panel: ['truncationRule', 'faciesProbability'],
      })
    }
  },
  { deep: true },
)
</script>
