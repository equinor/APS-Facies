<template>
  <v-container class="align justify center pa-0" fluid>
    <v-row>
      <v-col>
        <choose-grid-model />
      </v-col>
      <v-col>
        <choose-facies-realization-parameter v-if="currentGridModel" />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-expansion-panels
          v-if="currentGridModel"
          v-model="panels"
          variant="accordion"
          multiple
        >
          <v-expansion-panel expand value="zoneRegion" elevation="0">
            <v-expansion-panel-title>
              <section-title>Zones and Regions</section-title>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <zone-region v-if="currentGridModel" />
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
              <v-row v-if="currentGridModel" no-gutters>
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
                      {{ gridName }} has no blocked well parameters
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

import { ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing'
import { ref, computed } from 'vue'
import { useStore } from '../store'

const store = useStore()

// TODO: These were not in use...
const disabled = ref(false)
const readonly = ref(false)

const panels = computed<number[]>({
  get: () => {
    return store.getters['panels/selection']
  },
  set: (indices: number[]) =>
    store.dispatch('panels/change', { type: 'selection', indices }),
})

const hasWellParameters = computed<boolean>(() => {
  return store.state.parameters.blockedWell.available.length > 0
})

const hasBlockedWellParameter = computed<boolean>(() => {
  return !!store.getters.blockedWellParameter
})

const currentGridModel = computed<Optional<ID>>(() => {
  return store.state.gridModels.current
})

const gridName = computed<string>(() => {
  return store.getters.gridModel
})
</script>

<style lang="scss" scoped>
.v-expansion-panel-text {
  overflow: auto;
}
</style>
