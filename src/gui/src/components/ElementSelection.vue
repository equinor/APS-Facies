<template>
  <v-container
    align-start
    justify-start
  >
    <grid-model />
    <choose-facies-realization-parameter
      v-if="currentGridModel"
    />

    <v-expansion-panel
      v-if="currentGridModel"
      v-model="panel"
      expand
    >
      <v-expansion-panel-content>
        <div slot="header">
          <h2>Zones and regions</h2>
        </div>
        <v-card>
          <div v-if="currentGridModel">
            <zone-region />
          </div>
          <div v-else>
            Selection of zones and regions is not available until Grid Model is selected
          </div>
        </v-card>
      </v-expansion-panel-content>

      <v-expansion-panel-content>
        <div slot="header">
          <h2>Facies</h2>
        </div>
        <v-card>
          <div v-if="currentGridModel">
            <div
              v-if="hasWellParameters"
            >
              <choose-blocked-well-parameter />
              <choose-blocked-well-log-parameter
                v-if="hasBlockedWellParameter"
              />
              <div
                v-if="hasBlockedWellLogParameter"
              >
                <facies-selection />
              </div>
            </div>
            <div
              v-else
            >
              <facies-selection />
            </div>
          </div>
          <div v-else>
            Selection of facies is not available until Grid Model is selected
          </div>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
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

@Component({
  components: {
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

  get hasWellParameters (): boolean {
    return this.$store.state.parameters.blockedWell.available.length > 0
  }
  get hasBlockedWellLogParameter (): boolean {
    return !!this.$store.getters.blockedWellLogParameter
  }
  get hasBlockedWellParameter (): boolean {
    return !!this.$store.getters.blockedWellParameter
  }
  get currentGridModel (): boolean {
    return this.$store.state.gridModels.current
  }
  get panel (): boolean[] {
    return this.currentGridModel
      ? [true, true]
      : [false, false]
  }
}
</script>
