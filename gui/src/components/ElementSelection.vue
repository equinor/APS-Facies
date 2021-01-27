<template>
  <v-container
    class="align justify center"
    fluid
  >
    <v-row>
      <grid-model />
      <choose-facies-realization-parameter
        v-if="currentGridModel"
      />

      <v-expansion-panels
        v-if="currentGridModel"
        v-model="panels"
        accordion
        multiple
      >
        <v-expansion-panel
          expand
        >
          <v-expansion-panel-header>
            <section-title>Zones and Regions</section-title>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <zone-region
              v-if="currentGridModel"
            />
            <span v-else>
              Selection of zones and regions is not available until Grid Model is selected
            </span>
          </v-expansion-panel-content>
        </v-expansion-panel>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <section-title>Facies</section-title>
          </v-expansion-panel-header>
          <v-expansion-panel-content
            class="fill-height"
          >
            <v-row
              v-if="currentGridModel"
            >
              <v-row
                v-if="hasWellParameters"
                no-gutters
              >
                <v-col
                  class="pt-2"
                  cols="6"
                >
                  <choose-blocked-well-parameter />
                </v-col>
                <v-col
                  cols="6"
                  class="pt-2"
                >
                  <choose-blocked-well-log-parameter
                    v-if="hasBlockedWellParameter"
                  />
                </v-col>
                <v-col cols="12">
                  <facies-selection />
                </v-col>
              </v-row>
              <v-row
                v-else
                no-gutters
              >
                <v-col
                  cols="12"
                >
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
              Selection of facies is not available until Grid Model is selected
            </div>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ZoneRegion from '@/components/selection/ZoneRegionSelection.vue'
import GridModel from '@/components/selection/dropdown/ChooseGridModel.vue'
import FaciesSelection from '@/components/selection/FaciesSelection.vue'
import ChooseBlockedWellParameter from '@/components/selection/dropdown/ChooseBlockedWellParameter.vue'
import ChooseBlockedWellLogParameter from '@/components/selection/dropdown/ChooseBlockedWellLogParameter.vue'
import ChooseFaciesRealizationParameter from '@/components/selection/dropdown/ChooseFaciesRealizationParameter.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import { ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing'

@Component({
  components: {
    SectionTitle,
    ChooseFaciesRealizationParameter,
    ZoneRegion,
    GridModel,
    ChooseBlockedWellParameter,
    ChooseBlockedWellLogParameter,
    FaciesSelection,
  },
})
export default class ElementSelection extends Vue {
  disabled = false
  readonly = false

  get panels (): number[] { return this.$store.getters['panels/selection'] }
  set panels (indices) { this.$store.dispatch('panels/change', { type: 'selection', indices }) }

  get hasWellParameters (): boolean {
    return this.$store.state.parameters.blockedWell.available.length > 0
  }

  get hasBlockedWellParameter (): boolean {
    return !!this.$store.getters.blockedWellParameter
  }

  get currentGridModel (): Optional<ID> {
    return this.$store.state.gridModels.current
  }

  get gridName (): string { return this.$store.getters.gridModel }
}
</script>

<style lang="scss" scoped>
  .v-expansion-panel-content {
    overflow: auto;
  }
</style>
