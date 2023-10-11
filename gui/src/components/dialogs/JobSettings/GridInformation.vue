<template>
  <settings-panel v-if="!!$store.getters.gridModel" title="Grid information">
    <v-container
      v-if="!$store.getters['parameters/grid/waiting']"
      class="text-center"
    >
      <v-row class="fill" justify="space-around">
        <v-col cols="4">
          <numeric-field
            :model-value="gridSize.x"
            readonly
            discrete
            unit="cell"
            label="X"
            hint="The size of the grid"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="gridSize.y"
            readonly
            discrete
            unit="cell"
            label="Y"
            hint="The size of the grid"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="gridSize.z"
            readonly
            discrete
            unit="cell"
            label="Z"
            hint="The size of the grid"
            persistent-hint
          />
        </v-col>
        <v-spacer />
        <v-col cols="4">
          <numeric-field
            :model-value="simulationSettings.simulationBox.x"
            readonly
            label="X"
            unit="m"
            hint="The size of the simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationSettings.simulationBox.y"
            readonly
            label="Y"
            unit="m"
            hint="The size of the simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationSettings.simulationBox.z"
            readonly
            label="Z"
            unit="m"
            hint="The size of the simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationSettings.gridAzimuth"
            :ranges="{ min: -360, max: 360 }"
            readonly
            label="Grid azimuth"
            unit="°"
            hint="The angle between the grid, and UTM"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationSettings.simulationBoxOrigin.x"
            readonly
            label="X"
            unit="m"
            hint="Origin of simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationSettings.simulationBoxOrigin.y"
            readonly
            label="Y"
            unit="m"
            hint="Origin of simulation box"
            persistent-hint
          />
        </v-col>
      </v-row>
    </v-container>
    <v-container v-else>
      <v-row justify="center" align="center">
        <v-icon x-large v-text="$vuetify.icons.values.refreshSpinner" />
      </v-row>
    </v-container>
  </settings-panel>
</template>

<script setup lang="ts">
import NumericField from '@/components/selection/NumericField.vue'

import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'

import {
  Coordinate3D,
  SimulationSettings,
} from '@/utils/domain/bases/interfaces'

type Props = {
  gridSize: Coordinate3D
  simulationSettings: SimulationSettings
}
defineProps<Props>()
</script>
