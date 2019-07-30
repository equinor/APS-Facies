<template>
  <v-container
    align-start
    justify-start
  >
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
        <v-expansion-panel-content>
          <v-layout v-if="currentGridModel">
            <v-layout
              v-if="hasWellParameters"
              wrap
            >
              <v-flex xs6>
                <choose-blocked-well-parameter />
              </v-flex>
              <v-flex xs6>
                <choose-blocked-well-log-parameter
                  v-if="hasBlockedWellParameter"
                />
              </v-flex>
              <v-flex xs12>
                <facies-selection
                  v-if="hasBlockedWellLogParameter"
                />
              </v-flex>
            </v-layout>
          </v-layout>
          <div v-else>
            Selection of facies is not available until Grid Model is selected
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
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

@Component({
  components: {
    SectionTitle,
    ChooseFaciesRealizationParameter,
    ZoneRegion,
    GridModel,
    ChooseBlockedWellParameter,
    ChooseBlockedWellLogParameter,
    FaciesSelection
  },
})
export default class ElementSelection extends Vue {
  disabled: boolean = false
  readonly: boolean = false

  get panels (): number[] { return this.$store.getters['panels/selection'] }
  set panels (indices) { this.$store.dispatch('panels/change', { type: 'selection', indices }) }

  get hasWellParameters (): boolean {
    return this.$store.state.parameters.blockedWell.available.length > 0
  }
  get hasBlockedWellLogParameter (): boolean {
    return !!this.$store.getters.blockedWellLogParameter
  }
  get hasBlockedWellParameter (): boolean {
    return !!this.$store.getters.blockedWellParameter
  }
  get currentGridModel (): string {
    return this.$store.state.gridModels.current
  }
}
</script>

<style lang="scss" scoped>
  .v-expansion-panel-content {
    overflow: auto;
  }
</style>
