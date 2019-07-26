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
      v-model="panel"
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
          <div v-if="currentGridModel">
            <div
              v-if="hasWellParameters"
            >
              <choose-blocked-well-parameter />
              <choose-blocked-well-log-parameter
                v-if="hasBlockedWellParameter"
              />
              <facies-selection
                v-if="hasBlockedWellLogParameter"
              />
            </div>
          </div>
          <div v-else>
            Selection of facies is not available until Grid Model is selected
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

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

  panel: number[] = []

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

  @Watch('currentGridModel')
  onChangedGridModel (value: string) {
    if (value) {
      this.panel = [0, 1]
    }
  }
}
</script>

<style lang="scss" scoped>
  .v-expansion-panel-content {
    overflow: auto;
  }
</style>
