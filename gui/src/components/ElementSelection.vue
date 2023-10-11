<template>
  <v-container class="align justify center pa-0" fluid>
    <v-row>
      <v-col>
        <choose-grid-model />
      </v-col>
      <v-col>
        <choose-facies-realization-parameter v-if="gridModelSelected" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-expansion-panels
          v-if="gridModelSelected"
          v-model="expanded"
          variant="accordion"
          multiple
        >
          <v-expansion-panel expand value="zoneRegion" elevation="0">
            <v-expansion-panel-title>
              <section-title>Zones and Regions</section-title>
            </v-expansion-panel-title>
            <v-expansion-panel-text class="pa-0">
              <zone-region v-if="gridModelSelected" />
              <span v-else>
                Selection of zones and regions is not available until Grid Model
                is selected
              </span>
            </v-expansion-panel-text>
          </v-expansion-panel>
          <v-expansion-panel value="facies" elevation="0">
            <v-expansion-panel-title>
              <section-title>Facies</section-title>
            </v-expansion-panel-title>
            <v-expansion-panel-text class="fill-height">
              <v-row v-if="gridModelSelected" no-gutters>
                <v-row v-if="hasWellParameters" no-gutters>
                  <v-col class="pt-2" cols="6">
                    <choose-blocked-well-parameter />
                  </v-col>
                  <v-col cols="6" class="pt-2">
                    <choose-blocked-well-log-parameter
                      v-if="hasBlockedWellParameter"
                    />
                  </v-col>
                  <v-col cols="12">
                    <facies-selection />
                  </v-col>
                </v-row>
                <v-row v-else no-gutters>
                  <v-col cols="12">
                    <p class="text-center">
                      {{ currentGridModelName }} has no blocked well parameters
                    </p>
                  </v-col>
                  <v-col cols="12">
                    <facies-selection />
                  </v-col>
                </v-row>
              </v-row>
              <div v-else>
                Selection of facies is not available until Grid Model is
                selected
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import ZoneRegion from '@/components/selection/ZoneRegionSelection.vue'
import ChooseGridModel from '@/components/selection/dropdown/ChooseGridModel.vue'
import FaciesSelection from '@/components/selection/FaciesSelection.vue'
import ChooseBlockedWellParameter from '@/components/selection/dropdown/ChooseBlockedWellParameter.vue'
import ChooseBlockedWellLogParameter from '@/components/selection/dropdown/ChooseBlockedWellLogParameter.vue'
import ChooseFaciesRealizationParameter from '@/components/selection/dropdown/ChooseFaciesRealizationParameter.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import { computed } from 'vue'
import { usePanelStore } from '@/stores/panels'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useGridModelStore } from '@/stores/grid-models'

const parameterBlockedWellStore = useParameterBlockedWellStore()
const gridModelStore = useGridModelStore()

const panelStore = usePanelStore()
const expanded = computed({
  get: () => panelStore.getOpen('selection'),
  set: (panelNames: string[]) => {
    panelStore.setOpen('selection', panelNames)
  },
})

const hasWellParameters = computed<boolean>(
  () => parameterBlockedWellStore.available.length > 0,
)
const hasBlockedWellParameter = computed<boolean>(
  () => !!parameterBlockedWellStore.selected,
)
const currentGridModel = computed(() => gridModelStore.current)
const gridModelSelected = computed(() => !!currentGridModel.value)
const currentGridModelName = computed(() => currentGridModel.value?.name)
</script>

<style lang="scss" scoped>
.v-expansion-panel-text {
  overflow: auto;
}
</style>
