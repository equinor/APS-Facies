<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="550px"
    @keydown.esc="abort"
    @keydown.enter="choose"
  >
    <v-card
      v-if="fetched"
    >
      <v-card-title>
        <v-row>
          <v-col>
            <span class="text-h5">
              {{ `Export the APS model${ fmuMode ? ', and FMU settings' : '' }` }}
            </span>
          </v-col>
          <v-col cols="1">
            <icon-button
              v-tooltip="'Use defaults'"
              icon="refresh"
              color="primary"
              @click="() => restoreDefaults()"
            />
          </v-col>
        </v-row>
      </v-card-title>
      <v-card-text>
        <v-row>
          Paths are relative to the RMS project, which is currently located at {{ projectPath }}.
        </v-row>
        <v-row>
          <file-selection
            v-model="paths.model"
            label="Model file"
            :relative-to="projectPath"
            @update:error="err => setInvalid('model', err)"
          />
        </v-row>
        <div v-if="fmuMode">
          <v-row>
            <optional-file-selection
              v-model="paths.fmuConfig"
              v-tooltip="disabledMessage"
              label="FMU configuration file for APS model parameters"
              :disabled="!hasFmuUpdatableValues"
              :relative-to="projectPath"
              @update:error="err => setInvalid('fmuConfig', err)"
            />
          </v-row>
          <v-row>
            <optional-file-selection
              v-model="paths.probabilityDistribution"
              v-tooltip="disabledMessage"
              label="FMU configuration template for probability distributions"
              :disabled="!hasFmuUpdatableValues"
              :relative-to="projectPath"
              @update:error="err => setInvalid('probabilityDistribution', err)"
            />
          </v-row>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="blue darken-1"
          text
          :disabled="hasErrors"
          @click="choose"
        >
          Save
        </v-btn>
        <v-btn
          color="blue darken-1"
          text
          @click="abort"
        >
          Abort
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import AsyncComputed from 'vue-async-computed-decorator'

import { DEFAULT_MODEL_FILE_NAMES } from '@/config'

import rms from '@/api/rms'

import FileSelection from '@/components/selection/FileSelection.vue'
import OptionalFileSelection from '@/components/selection/OptionalFileSelection.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { APSError } from '@/utils/domain/errors'
import { Paths } from '@/api/types'

interface State {
  path: string
  disabled: boolean
}

interface PathsState {
  model: string
  fmuConfig: State
  probabilityDistribution: State
}

interface Invalid {
  model: boolean
  fmuConfig: boolean
  probabilityDistribution: boolean
}

@Component({
  components: {
    IconButton,
    FileSelection,
    OptionalFileSelection,
  },
})
export default class ExportDialog extends Vue {
  dialog = false
  resolve: ((value: { paths: Paths | null }) => void) | null = null
  reject: ((reason: string) => void) | null = null
  fetched = false
  disabled = false
  projectPath = ''
  paths: PathsState = {
    model: '',
    fmuConfig: { path: '', disabled: true },
    probabilityDistribution: { path: '', disabled: true },
  }

  invalid: Invalid = {
    model: false,
    fmuConfig: false,
    probabilityDistribution: false,
  }

  setInvalid (name: string, error: boolean): void {
    this.invalid[`${name}`] = error
  }

  async mounted (): Promise<void> {
    await this.updateProjectPath()
    await this.restoreDefaults()
    this.fetched = true
  }

  @AsyncComputed({
    default: true,
  })
  async hasFmuUpdatableValues (): Promise<boolean> {
    const model = (this as ExportDialog).$store.getters['modelFileExporter/model']
    if (!model) return new Promise(resolve => resolve(false))
    return rms.hasFmuUpdatableValues(model)
  }

  get fmuMode (): boolean { return this.$store.getters.fmuUpdatable }

  get hasErrors (): boolean {
    if (!this.hasFmuUpdatableValues) return this.invalid.model

    return Object.keys(this.invalid)
      .filter(key => !this.paths[`${key}`].disabled)
      .some(key => this.invalid[`${key}`])
  }

  get disabledMessage (): string | undefined {
    if (!this.hasFmuUpdatableValues) {
      return 'No variables are marked as FMU updatable'
    } else return undefined
  }

  async defaultPaths (): Promise< PathsState > {
    const { model, fmuConfig, probabilityDistribution } = DEFAULT_MODEL_FILE_NAMES
    const useNonStandardFmu = this.$store.state.fmu.useNonStandardFmu.value
    const defaultRelativeExportPaths = await rms.apsFmuConfig(useNonStandardFmu)
    const modelPath = defaultRelativeExportPaths[0]
    const ertParamPath = defaultRelativeExportPaths[1]
    const fmuParamPath = defaultRelativeExportPaths[2]
    return {
      model: `${modelPath}/${model}`,
      fmuConfig: {
        path: `${fmuParamPath}/${fmuConfig}`,
        disabled: false,
      },
      probabilityDistribution: {
        path: `${ertParamPath}/${probabilityDistribution}`,
        disabled: false,
      },
    }
  }

  async open (): Promise<{ paths: Paths | null }> {
    this.dialog = true
    this.$asyncComputed.hasFmuUpdatableValues.update()
    await this.updateProjectPath()
    await this.restoreDefaults()
    return new Promise((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
  }

  choose (): void {
    if (!this.resolve) throw new APSError('resolve has not been set')
    if (!this.paths.model) throw new APSError('path has not been set')

    const get = (item: State): string | null => item.disabled ? null : item.path

    const paths: Paths = !this.hasFmuUpdatableValues
      ? {
        model: this.paths.model,
        fmuConfig: null,
        probabilityDistribution: null,
      }
      : {
        model: this.paths.model,
        fmuConfig: get(this.paths.fmuConfig),
        probabilityDistribution: get(this.paths.probabilityDistribution),
      }
    this.resolve({ paths })
    this.dialog = false

  }

  abort (): void {
    if (!this.resolve) throw new APSError('resolve has not been set')

    this.resolve({ paths: null })
    this.dialog = false
  }

  async restoreDefaults (): Promise<void> {
    this.paths = await this.defaultPaths()
  }

  async updateProjectPath (): Promise<void> {
    this.projectPath = await rms.projectDirectory()
  }
}
</script>
