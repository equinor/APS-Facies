<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="550px"
    @keydown.esc="abort"
    @keydown.enter="choose"
  >
    <v-card v-if="fetched">
      <v-card-title>
        <v-row>
          <v-col>
            <span class="text-h5">
              {{ `Export the APS model${fmuMode ? ', and FMU settings' : ''}` }}
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
          Paths are relative to the RMS project, which is currently located at
          <pre>{{ projectPath }}</pre>
          .
        </v-row>
        <v-row>
          <file-selection
            v-model="pathsState.model.path"
            label="Model file"
            :relative-to="projectPath"
            @update:error="(err: boolean) => setInvalid('model', err)"
          />
        </v-row>
        <div v-if="fmuMode">
          <v-row>
            <optional-file-selection
              v-model="pathsState.fmuConfig"
              v-tooltip="disabledMessage"
              label="FMU configuration file for APS model parameters"
              :disabled="!_hasFmuUpdatableValues"
              :relative-to="projectPath"
              @update:error="(err: boolean) => setInvalid('fmuConfig', err)"
            />
          </v-row>
          <v-row>
            <optional-file-selection
              v-model="pathsState.probabilityDistribution"
              v-tooltip="disabledMessage"
              label="FMU configuration template for probability distributions"
              :disabled="!_hasFmuUpdatableValues"
              :relative-to="projectPath"
              @update:error="
                (err: boolean) => setInvalid('probabilityDistribution', err)
              "
            />
          </v-row>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="blue-darken-1"
          variant="text"
          :disabled="hasErrors"
          @click="choose"
        >
          Save
        </v-btn>
        <v-btn color="blue-darken-1" variant="text" @click="abort">
          Abort
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { DEFAULT_MODEL_FILE_NAMES } from '@/config'

import rms from '@/api/rms'

import FileSelection from '@/components/selection/FileSelection.vue'
import OptionalFileSelection from '@/components/selection/OptionalFileSelection.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { APSError } from '@/utils/domain/errors'
import type { Paths } from '@/api/types'
import { ref, onMounted, computed, watch } from 'vue'
import { useFmuOptionStore } from '@/stores/fmu/options'
import { useModelFileExporterStore } from '@/stores/model-file-exporter'

interface State {
  path: string
  disabled: boolean
}

interface PathsState {
  model: State
  fmuConfig: State
  probabilityDistribution: State
}

type Invalid = Record<keyof PathsState, boolean>

const fmuOptionStore = useFmuOptionStore()

const dialog = ref(false)
const resolve = ref<((value: { paths: Paths | null }) => void) | null>(null)
const reject = ref<((reason: string) => void) | null>(null)
const fetched = ref(false)
const projectPath = ref('')
const pathsState = ref<PathsState>({
  model: { path: '', disabled: false },
  fmuConfig: { path: '', disabled: true },
  probabilityDistribution: { path: '', disabled: true },
})

const invalid = ref<Invalid>({
  model: false,
  fmuConfig: false,
  probabilityDistribution: false,
})

function setInvalid(name: keyof Invalid, error: boolean): void {
  invalid.value[name] = error
}

onMounted(async () => {
  await updateProjectPath()
  await restoreDefaults()
  fetched.value = true
})

const _hasFmuUpdatableValues = ref(false)

async function checkFmuUpdatableValues() {
  const { model } = useModelFileExporterStore()
  _hasFmuUpdatableValues.value = !model
    ? false
    : await rms.hasFmuUpdatableValues(model)
}

watch(dialog, async (value: boolean) => {
  if (value) await checkFmuUpdatableValues()
})

const fmuMode = computed(
  () =>
    fmuOptionStore.options.runFmuWorkflows ||
    fmuOptionStore.options.onlyUpdateFromFmu,
)
const hasErrors = computed(() => {
  if (!_hasFmuUpdatableValues.value) return invalid.value.model

  return (Object.keys(invalid.value) as (keyof Invalid)[])
    .filter((key) => !pathsState.value[key].disabled)
    .some((key) => invalid.value[key])
})

const disabledMessage = computed<string | undefined>(() => {
  return !_hasFmuUpdatableValues.value
    ? 'No variables are marked as FMU updatable'
    : undefined
})

async function defaultPaths(): Promise<PathsState> {
  const { model, fmuConfig, probabilityDistribution } = DEFAULT_MODEL_FILE_NAMES
  const [modelPath, ertParamPath, fmuParamPath] = await rms.apsFmuConfig(
    fmuOptionStore.options.useNonStandardFmu,
  )
  if (!projectPath.value) {
    await updateProjectPath()
  }
  return {
    model: {
      path: `${projectPath.value}/${modelPath}/${model}`,
      disabled: false,
    },
    fmuConfig: {
      path: `${projectPath.value}/${fmuParamPath}/${fmuConfig}`,
      disabled: false,
    },
    probabilityDistribution: {
      path: `${projectPath.value}/${ertParamPath}/${probabilityDistribution}`,
      disabled: false,
    },
  }
}

async function open(): Promise<{ paths: Paths | null }> {
  dialog.value = true
  // call hasFmuUpdatableValues
  await updateProjectPath()
  await restoreDefaults()
  return new Promise((_resolve, _reject) => {
    resolve.value = _resolve
    reject.value = _reject
  })
}
defineExpose({ open })

function choose(): void {
  if (!resolve.value) throw new APSError('resolve has not been set')
  if (!pathsState.value) throw new APSError('path has not been set')

  const getPath = (item: State): string | null =>
    item.disabled ? null : item.path

  const paths: Paths = !_hasFmuUpdatableValues.value
    ? {
        model: pathsState.value.model.path,
        fmuConfig: null,
        probabilityDistribution: null,
      }
    : {
        model: pathsState.value.model.path,
        fmuConfig: getPath(pathsState.value.fmuConfig),
        probabilityDistribution: getPath(
          pathsState.value.probabilityDistribution,
        ),
      }
  resolve.value?.({ paths })
  dialog.value = false
}

function abort(): void {
  if (!resolve.value) throw new APSError('resolve has not been set')

  resolve.value({ paths: null })
  dialog.value = false
}

async function restoreDefaults(): Promise<void> {
  pathsState.value = await defaultPaths()
}

async function updateProjectPath(): Promise<void> {
  projectPath.value = await rms.projectDirectory()
}
</script>
