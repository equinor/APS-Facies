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

import type { Facies, Region } from '@/utils/domain'
import  { Zone } from '@/utils/domain'
import { computed, watch } from 'vue'
import { usePanelStore } from '@/stores/panels'
import { useRegionStore } from '@/stores/regions'
import { useOptionStore } from '@/stores/options'
import { useZoneStore } from '@/stores/zones'
import { useFaciesStore } from '@/stores/facies'

const optionStore = useOptionStore()
const zoneStore = useZoneStore()
const regionStore = useRegionStore()
const faciesStore = useFaciesStore()
const panelStore = usePanelStore()

const expanded = computed({
  get: () => panelStore.getOpen('settings'),
  set: (panelNames: string[]) => panelStore.setOpen('settings', panelNames),
})

const options = computed(() => optionStore.options.showNameOrNumber)

const title = computed<string>(() => {
  let title = ''
  const zone = zoneStore.current
  if (zone) {
    title = `Settings for ${getNameOrCode(zone)}`
    const region = regionStore.current;
    if (regionStore.use && region) {
      title += ` / ${getNameOrCode(region)}`
    }
  }
  return title
})

function getNameOrCode(item: Zone | Region): string | number {
  const nameOrNumber = optionStore.options.showNameOrNumber[item instanceof Zone ? 'zone' : 'region']
  if (nameOrNumber === 'name') return item.name
  return `${item instanceof Zone ? 'Zone' : 'Region'} ${item.code}`
}

const _facies = computed<Facies[]>(() => faciesStore.selected)
const hasFacies = computed<boolean>(() => _facies.value.length > 0)
const minFacies = 2
const hasEnoughFacies = computed<boolean>(() => _facies.value.length >= minFacies)

watch(
  _facies,
  async () => {
    panelStore.set('settings', 'truncationRule', hasEnoughFacies.value)

    if (!hasFacies.value) {
      panelStore.close('settings', 'truncationRule')
      panelStore.close('settings', 'faciesProbability')
    }
  },
  { deep: true },
)
</script>
