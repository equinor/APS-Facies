<template>
  <v-dialog v-model="dialog" persistent max-width="500px" @keydown.esc="cancel">
    <v-card>
      <v-card-title>
        <span class="text-h5"> Visualization settings </span>
      </v-card-title>
      <v-card-text>
        <v-row>
          <!--Seed-->
          <v-col cols="10">
            <numeric-field
              v-model="settings.seed"
              :ranges="{ min: 0, max: Math.pow(2, 64) - 1 }"
              label="Seed"
            />
          </v-col>
          <v-col cols="2">
            <icon-button icon="random" @click="settings.seed = newSeed()" />
          </v-col>
        </v-row>
        <v-col cols="6">
          <v-checkbox
            v-model="settings.gridModel.use"
            label="Use model grid"
          />
        </v-col>
        <v-col cols="6" />
        <v-row v-if="settings.gridModel.use" justify="space-around">
          <v-col cols="4">
            <numeric-field
              v-model="settings.gridModel.size.x"
              discrete
              unit="cell"
              label="X"
              hint="The size of the grid to be simulated"
              persistent-hint
            />
          </v-col>
          <v-col cols="4">
            <numeric-field
              v-model="settings.gridModel.size.y"
              discrete
              unit="cell"
              label="Y"
              hint="The size of the grid to be simulated"
              persistent-hint
            />
          </v-col>
          <v-col cols="4">
            <numeric-field
              v-model="settings.gridModel.size.z"
              discrete
              unit="cell"
              label="Z"
              hint="The size of the grid to be simulated"
              persistent-hint
            />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="blue darken-1" variant="text" @click="cancel">
          Close
        </v-btn>
        <v-btn color="blue darken-1" variant="text" @click="save"> Save </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import APSError from '@/utils/domain/errors/base'

import type { DialogOptions } from '@/utils/domain/bases/interfaces'
import type { Optional } from '@/utils/typing'
import type { Color } from '@/utils/domain/facies/helpers/colors'

import NumericField from '@/components/selection/NumericField.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { newSeed } from '@/utils'
import { ref } from 'vue'
import { useTheme } from 'vuetify'
import type { Settings } from '@/utils/domain/gaussianRandomField'

type ReturnValue  = {
  save: true
  settings: Settings
} | {
  save: false,
  settings: null
}

const dialog = ref(false)
const resolve = ref<Optional<({ save, settings }: ReturnValue) => void>>(null)
const reject = ref<Optional<({ save, settings }: ReturnValue) => void>>(null)
const settings = ref<Settings | {
  crossSection : {
    type: null
  },
  gridModel: Settings['gridModel']
  seed: null
}>({
  crossSection: {
    type: null,
  },
  gridModel: {
    use: false,
    size: {
      x: 100,
      y: 100,
      z: 1,
    },
  },
  seed: null,
})

const theme = useTheme()

const options = ref<DialogOptions>({
  color: theme.global.current.value.colors.primary as Color,
  width: 290,
})

async function open(newSettings: Settings, newOptions: DialogOptions = {}): Promise<ReturnValue> {
  dialog.value = true
  settings.value = newSettings
  options.value = { ...options.value, ...newOptions }
  return new Promise((_resolve, _reject) => {
    resolve.value = _resolve
    reject.value = _reject
  })
}
defineExpose({ open })

function save(): void {
  if (!resolve.value)
    throw new APSError('The `resolve` callback has not been set')
  resolve.value({ save: true, settings: settings.value as Settings })
  dialog.value = false
}

function cancel(): void {
  if (!resolve.value)
    throw new APSError('The `resolve` callback has not been set')
  resolve.value({ save: false, settings: null })
  dialog.value = false
}
</script>
