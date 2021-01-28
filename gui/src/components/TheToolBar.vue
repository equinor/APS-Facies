<template>
  <v-toolbar
    flat
    :color="'#ffffff'"
  >
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

    <export-dialog
      ref="exportDialog"
    />

    <v-spacer />

    <v-row
      v-if="isDevelop"
    >
      <load-job />

      <run-job />

      <export-state />
    </v-row>

    <job-settings />

    <v-btn
      v-if="false"
      disabled
      outlined
      color="primary"
    >
      Run Settings
    </v-btn>
    <v-popover
      trigger="hover"
    >
      <icon-button
        icon="changelog"
        color="primary"
        @click="() => openChangelog()"
      />
      <span slot="popover">
        What's new?
      </span>
    </v-popover>
    <changelog-dialog ref="changelogDialog" />
    <v-popover
      trigger="hover"
    >
      <icon-button
        icon="help"
        color="primary"
        @click="() => goToHelp()"
      />
      <span slot="popover">
        Documentation of the APS methodology and user guide for this plug-in.
      </span>
    </v-popover>
    <span
      v-if="betaBuild"
    >
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

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Store } from '@/store/typing'
import { displayError, displaySuccess } from '@/utils/helpers/storeInteraction'

import { xml2json } from 'xml-js'

import ExportDialog from '@/components/dialogs/ExportDialog.vue'
import ChangelogDialog from '@/components/dialogs/ChangelogDialog.vue'
import JobSettings from '@/components/dialogs/JobSettings/index.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ExportState from '@/components/debugging/exportState.vue'
import LoadJob from '@/components/debugging/LoadJob.vue'
import RunJob from '@/components/debugging/RunJob.vue'

import { Optional } from '@/utils/typing'

import rms from '@/api/rms'
import { resetState } from '@/store'
import { isDevelopmentBuild } from '@/utils/helpers/simple'

async function loadModelFile (store: Store, fileName: string, fileContent: string | null = null): Promise<void> {
  let json: string | null = null

  store.commit('LOADING', { loading: true, message: `Checking the model file, "${fileName}", for consistency` }, { root: true })
  if (!fileContent) fileContent = await rms.loadFile(fileName)

  if (!fileContent) {
    await displayError('The file is empty, or it does not exist')
  } else {
    try {
      json = xml2json(fileContent, { compact: false, ignoreComment: true })
    } catch (err) {
      await displayError(
        'The file you tried to open is not valid XML and cannot be used\n'
        + 'Fix the following error before opening again:\n\n'
        + err.message
      )
    }
    if (json) {
      const { valid, error } = await rms.isApsModelValid(btoa(fileContent))
      if (valid) {
        resetState()
        store.commit('LOADING', { loading: true, message: 'Resetting the state...' }, { root: true })
        await store.dispatch('fetch')
        await store.dispatch('modelFileLoader/populateGUI', { json, fileName })
      } else {
        await displayError(
          'The file you tried to open is not a valid APS model file and cannot be used\n'
          + 'Fix the following error before opening again:\n\n'
          + error
        )
      }
    }
  }

  store.commit('LOADING', { loading: false }, { root: true })
}

@Component({
  components: {
    ExportState,
    ExportDialog,
    JobSettings,
    IconButton,
    ChangelogDialog,
    LoadJob,
    RunJob,
  },
})
export default class TheToolBar extends Vue {
  refreshing = false

  lastMSelectedModelFile = ''

  get betaBuild (): boolean { return process.env.VUE_APP_BUILD_MODE !== 'stable' }

  get versionNumber (): Optional<string> { return process.env.VUE_APP_APS_VERSION || null }

  get buildNumber (): Optional<string> { return process.env.VUE_APP_BUILD_NUMBER || null }

  get commitHash (): Optional<string> { return process.env.VUE_APP_HASH || null }

  get versionInformation (): string {
    return this.versionNumber && this.buildNumber && this.commitHash
      ? `${this.versionNumber}.${this.buildNumber}-${this.commitHash} (beta)`
      : 'live'
  }

  get isDevelop (): boolean { return isDevelopmentBuild() }

  goToHelp (): void {
    rms.openWikiHelp()
  }

  openChangelog (): void {
    (this.$refs.changelogDialog as ChangelogDialog).open()
  }

  async importModelFile (): Promise<void> {
    if (isDevelopmentBuild()) {
      const input = document.createElement('input')
      input.type = 'file'
      input.onchange = (event: Event): void => {
        const { files } = (event.target as HTMLInputElement)
        if (files) {
          const file = files[0]
          file.text().then(content => loadModelFile(this.$store, file.name, content))
        }
      }
      input.click()
      document.removeChild(input)
    } else {
      const fileName = await rms.chooseFile('load', 'APS model files (*.xml)', this.lastMSelectedModelFile)
      if (fileName) {
        this.lastMSelectedModelFile = fileName
        await loadModelFile(this.$store, fileName)
      }
    }
  }

  async refresh (): Promise<void> {
    this.refreshing = true
    await this.$store.dispatch('refresh', 'Fetching data from RMS')
    this.refreshing = false
  }

  async exportModelFile (): Promise<void> {
    const exportedXMLString = await this.$store.dispatch('modelFileExporter/createModelFileFromStore', {})
      .catch(async error => {
        await displayError(error.message)
      })
    if (exportedXMLString) {
      const result = await rms.isApsModelValid(btoa(exportedXMLString))
      if (result.valid) {
        (this.$refs.exportDialog as ExportDialog).open()
          .then(({ paths }) => {
            if (paths) {
              const resultPromise = rms.saveModel(btoa(exportedXMLString), paths)
              resultPromise.then(async (success: boolean): Promise<void> => {
                if (success) {
                  await displaySuccess(`The model file was saved to ${paths.model}`)
                }
              })
            }
          })
      } else {
        await displayError(
          'The model you have defined is not valid and cannot be exported\n'
            + 'Fix the following error before exporting again:\n\n'
            + result.error
        )
      }
    }
  }
}
</script>
