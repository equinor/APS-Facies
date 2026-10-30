<template>
  <div>
    <header
      class="settings-header position-sticky top-0 bg-surface d-flex align-center pa-2"
    >
      <section-title>{{ title }}</section-title>
    </header>
    <v-expansion-panels v-model="expanded" variant="accordion" multiple>
      <v-expansion-panel
        value="faciesProbability"
        :disabled="!hasFacies"
        elevation="0"
      >
        <v-expansion-panel-title class="px-2">
          <section-title>Probabilities for Facies</section-title>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <facies-probability-cube />
        </v-expansion-panel-text>
        <p v-if="!hasFacies" class="px-2 pb-3 text-caption">
          No Facies has been selected
        </p>
      </v-expansion-panel>
      <v-expansion-panel
        v-tooltip.bottom="{
          content: !hasEnoughFacies && 'Too few Facies has been selected',
          disabled: hasEnoughFacies,
        }"
        value="truncationRule"
        :disabled="!hasEnoughFacies"
        elevation="0"
      >
        <template #title>
          <section-title>Truncation Rule</section-title>
        </template>
        <template #text>
          <truncation-rule />
        </template>
      </v-expansion-panel>
      <gaussian-random-fields />
    </v-expansion-panels>
  </div>
</template>

<script setup lang="ts">
import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple.vue'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube/index.vue'
import TruncationRule from '@/components/specification/TruncationRule/index.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import type { Facies, Region } from '@/utils/domain'
import { Zone } from '@/utils/domain'
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

const title = computed<string>(() => {
  let title = ''
  const zone = zoneStore.current as Zone
  if (zone) {
    title = `Settings for ${getNameOrCode(zone)}`
    const region = regionStore.current as Region
    if (regionStore.use && region) {
      title += ` / ${getNameOrCode(region)}`
    }
  }
  return title
})

function getNameOrCode(item: Zone | Region): string | number {
  const nameOrNumber =
    optionStore.options.showNameOrNumber[
      item instanceof Zone ? 'zone' : 'region'
    ]
  if (nameOrNumber === 'name') return item.name
  return `${item instanceof Zone ? 'Zone' : 'Region'} ${item.code}`
}

const _facies = computed<Facies[]>(() => faciesStore.selected)
const hasFacies = computed<boolean>(() => _facies.value.length > 0)
const minFacies = 2
const hasEnoughFacies = computed<boolean>(
  () => _facies.value.length >= minFacies,
)

watch(_facies, () => {
  panelStore.set('settings', 'faciesProbability', hasFacies.value)
  if (!hasEnoughFacies.value) panelStore.close('settings', 'truncationRule')
})
</script>

<style lang="scss" scoped>
.settings-header {
  z-index: 2;
  border-bottom: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>
