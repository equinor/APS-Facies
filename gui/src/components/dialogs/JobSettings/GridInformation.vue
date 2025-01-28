<template>
  <settings-panel v-if="!!gridModelStore.current" title="Grid information">
    <v-container v-if="!parameterGridModelStore.waiting" class="text-center">
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
      </v-row>
      <v-spacer />
      <v-row
        v-if="parameterSimboxStore.waiting"
        justify="center"
        align="center"
      >
        <v-icon size="x-large" :icon="$vuetify.icons.aliases?.refreshSpinner" />
      </v-row>
      <v-row v-else>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationBox.x"
            readonly
            label="X"
            unit="m"
            hint="The size of the simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationBox.y"
            readonly
            label="Y"
            unit="m"
            hint="The size of the simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationBox.z"
            readonly
            label="Z"
            unit="m"
            :hint="simulationBox.hint"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="gridAzimuth"
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
            :model-value="simulationBoxOrigin.x"
            readonly
            label="X"
            unit="m"
            hint="Origin of simulation box"
            persistent-hint
          />
        </v-col>
        <v-col cols="4">
          <numeric-field
            :model-value="simulationBoxOrigin.y"
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
        <v-icon size="x-large" :icon="$vuetify.icons.aliases?.refreshSpinner" />
      </v-row>
    </v-container>
  </settings-panel>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import NumericField from '@/components/selection/NumericField.vue'

import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'

import type { Coordinate3D } from '@/utils/domain/bases/interfaces'
import { useParameterGridStore } from '@/stores/parameters/grid'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterGridSimulationBoxStore } from '@/stores/parameters/grid/simulation-box'
import { useZoneStore } from '@/stores/zones'

const gridModelStore = useGridModelStore()
const parameterGridModelStore = useParameterGridStore()
const parameterSimboxStore = useParameterGridSimulationBoxStore()
const zoneStore = useZoneStore()

const gridSize = computed<Coordinate3D>(() => parameterGridModelStore.size)
const gridAzimuth = computed(() => parameterGridModelStore.azimuth)
const simulationBoxOrigin = computed(() => parameterSimboxStore.origin)
const simulationBox = computed<Coordinate3D & { hint: string }>(() => {
  const z = parameterSimboxStore.size.z
  let hint: string = 'The height of the simulation box'
  let zValue: number
  if (z !== null) {
    if (typeof z === 'object') {
      if (zoneStore.current) {
        zValue = z[zoneStore.current.code]
        hint = `The height of the simulation box in zone '${zoneStore.current.name}'`
      } else {
        zValue = Math.max(...Object.values(z))
        hint = 'The maximum height of the simulation box in any zone'
      }
    } else {
      zValue = z
      hint = 'The height of the simulation box'
    }
  } else {
    zValue = 0
    hint = 'Unknown height of the simulation box'
  }
  return {
    ...parameterSimboxStore.size,
    z: zValue,
    hint,
  }
})
</script>
