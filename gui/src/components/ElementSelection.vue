<template>
  <v-container class="align justify center pa-0" fluid>
    <v-row>
      <v-col>
        <v-expansion-panels v-model="expanded" variant="accordion" multiple>
          <v-expansion-panel value="general" elevation="0">
            <v-expansion-panel-title class="px-2">
              <section-title>General</section-title>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="d-flex flex-column ga-3 px-2 pb-2">
                <choose-grid-model />
                <choose-facies-realization-parameter
                  :disabled="!gridModelSelected"
                  disabled-message="Selection of a Facies Realization parameter is not available until a Grid Model is selected"
                />
                <model-file-actions />
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
          <v-expansion-panel
            value="zoneRegion"
            :disabled="!gridModelSelected"
            elevation="0"
          >
            <v-expansion-panel-title class="px-2">
              <section-title>Zones and Regions</section-title>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <zone-region />
            </v-expansion-panel-text>
            <p v-if="!gridModelSelected" class="px-2 pb-3 text-caption">
              Selection of zones and regions is not available until a Grid Model
              is selected
            </p>
          </v-expansion-panel>
          <v-expansion-panel
            value="facies"
            :disabled="!gridModelSelected"
            elevation="0"
          >
            <v-expansion-panel-title class="px-2">
              <section-title>Facies</section-title>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <v-row no-gutters class="fill-height">
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
            </v-expansion-panel-text>
            <p v-if="!gridModelSelected" class="px-2 pb-3 text-caption">
              Selection of facies is not available until a Grid Model is selected
            </p>
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
import ModelFileActions from '@/components/selection/ModelFileActions.vue'
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
