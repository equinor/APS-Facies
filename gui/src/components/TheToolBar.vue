<template>
  <v-toolbar color="#ffffff">
    <!--
      NOTE: the attribute 'flat' has been replaced with 'color=""', as to avoid  mutating a prop directly
      This is *exactly* the same as what's done in the source code for the upload button
    -->
    <icon-button
      ref="uploadButton"
      v-tooltip.bottom="'Import an existing model file'"
      color="black"
      icon="import"
      @click="importModelFile"
    />
    <icon-button
      v-tooltip.bottom="'Export the current specification as a model file'"
      icon="export"
      @click="exportModelFile"
    />
    <export-dialog ref="exportDialog" />
    <v-spacer />
    <v-row v-if="isDevelop">
      <load-job />
      <run-job />
      <export-state />
    </v-row>
    <job-settings />
    <v-btn v-if="false" disabled variant="outlined" color="primary"> Run Settings </v-btn>
    <icon-button
      icon="changelog"
      color="primary"
      v-tooltip.bottom="`What's new?`"
      @click="() => openChangelog()"
    />
    <changelog-dialog ref="changelogDialog" />
    <icon-button
      icon="help"
      color="primary"
      @click="() => goToHelp()"
      v-tooltip="
        'Documentation of the APS methodology and user guide for this plug-in.'
      "
    />
    <span v-if="betaBuild">
      {{ `${versionInformation}` }}
    </span>
    <icon-button
      v-tooltip.bottom="'Refreshes the data gathered from RMS'"
      icon="refresh"
      :waiting="refreshing"
      @click="refresh"
    />
  </v-toolbar>
</template>

<script setup lang="ts">
import { Store } from '@/store/typing'
import { displayError, displaySuccess } from '@/utils/helpers/storeInteraction'
import ExportDialog from '@/components/dialogs/ExportDialog.vue'
import ChangelogDialog from '@/components/dialogs/ChangelogDialog.vue'
import JobSettings from '@/components/dialogs/JobSettings/index.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ExportState from '@/components/debugging/exportState.vue'
import LoadJob from '@/components/debugging/LoadJob.vue'
import RunJob from '@/components/debugging/RunJob.vue'
import { Optional } from '@/utils/typing'
import rms from '@/api/rms'
import { resetState, useStore } from '@/store'
import { isDevelopmentBuild } from '@/utils/helpers/simple'
import { ref } from 'vue'
import { XMLParser } from 'fast-xml-parser'

const betaBuild: boolean = import.meta.env.VUE_APP_BUILD_MODE !== 'stable'
const versionNumber: Optional<string> =
  import.meta.env.VUE_APP_APS_VERSION || null
const buildNumber: Optional<string> =
  import.meta.env.VUE_APP_BUILD_NUMBER || null
const commitHash: Optional<string> = import.meta.env.VUE_APP_HASH || null
const versionInformation: string =
  versionNumber && buildNumber && commitHash
    ? `${versionNumber}.${buildNumber}-${commitHash} (beta)`
    : 'live'
const isDevelop = isDevelopmentBuild()

async function loadModelFile(
  store: Store,
  fileName: string,
  fileContent: string | null = null,
): Promise<void> {
  let json: string | null = null

  store.commit(
    'LOADING',
    {
      loading: true,
      message: `Checking the model file, "${fileName}", for consistency`,
    },
    { root: true },
  )
  if (!fileContent) fileContent = await rms.loadFile(fileName)

  if (!fileContent) {
    await displayError('The file is empty, or it does not exist')
  } else {
    try {
      // TODO: Check whether this new XML parser actually outputs similar json.
      // json = xml2json(fileContent, { compact: false, ignoreComment: true });
      const xmlParser = new XMLParser()
      const jsObject = xmlParser.parse(fileContent)
      json = JSON.stringify(jsObject)
    } catch (err: any) {
      await displayError(
        'The file you tried to open is not valid XML and cannot be used\n' +
          'Fix the following error before opening again:\n\n' +
          err.message,
      )
    }
    if (json) {
      const { valid, error } = await rms.isApsModelValid(btoa(fileContent))
      if (valid) {
        resetState()
        store.commit(
          'LOADING',
          { loading: true, message: 'Resetting the state...' },
          { root: true },
        )
        await store.dispatch('fetch')
        await store.dispatch('modelFileLoader/populateGUI', { json, fileName })
      } else {
        await displayError(
          'The file you tried to open is not a valid APS model file and cannot be used\n' +
            'Fix the following error before opening again:\n\n' +
            error,
        )
      }
    }
  }

  store.commit('LOADING', { loading: false }, { root: true })
}

const store = useStore()

const refreshing = ref(false)
const lastMSelectedModelFile = ref('')
const changelogDialog = ref<InstanceType<typeof ChangelogDialog> | null>(null)
const exportDialog = ref<InstanceType<typeof ExportDialog> | null>(null)

function goToHelp(): void {
  rms.openWikiHelp()
}

function openChangelog(): void {
  changelogDialog.value?.open()
}

async function importModelFile(): Promise<void> {
  if (isDevelop) {
    const input = document.createElement('input')
    input.type = 'file'
    input.onchange = (event: Event): void => {
      const { files } = event.target as HTMLInputElement
      if (files) {
        const file = files[0]
        file.text().then((content) => loadModelFile(store, file.name, content))
      }
    }
    input.click()
    document.removeChild(input)
  } else {
    const fileName = await rms.chooseFile(
      'load',
      'APS model files (*.xml)',
      lastMSelectedModelFile.value,
    )
    if (fileName) {
      lastMSelectedModelFile.value = fileName
      await loadModelFile(store, fileName)
    }
  }
}

async function refresh(): Promise<void> {
  refreshing.value = true
  await store.dispatch('refresh', 'Fetching data from RMS')
  refreshing.value = false
}

async function exportModelFile(): Promise<void> {
  const exportedXMLString = await store
    .dispatch('modelFileExporter/createModelFileFromStore', {})
    .catch(async (error) => {
      await displayError(error.message)
    })
  if (exportedXMLString) {
    const result = await rms.isApsModelValid(btoa(exportedXMLString))
    if (result.valid) {
      const response = await exportDialog.value?.open()
      if (response?.paths) {
        const resultPromise = rms.saveModel(
          btoa(exportedXMLString),
          response.paths,
        )
        resultPromise.then(async (success: boolean): Promise<void> => {
          if (success) {
            await displaySuccess(
              `The model file was saved to ${response.paths?.model ?? '-'}`,
            )
          }
        })
      }
    } else {
      await displayError(
        'The model you have defined is not valid and cannot be exported\n' +
          'Fix the following error before exporting again:\n\n' +
          result.error,
      )
    }
  }
}
</script>
