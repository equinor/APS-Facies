<template>
  <v-toolbar
    flat
    :color="'#ffffff'"
  >
    <!--
      NOTE: the attribute 'flat' has been replaced with 'color=""', as to avoid  mutating a prop directly
      This is *exactly* the same as what's done in the source code for the upload button
    -->
    <upload-button
      ref="uploadButton"
      v-tooltip.bottom="'Import an existing model file'"
      color=""
      icon
      @file-update="importModelFile"
    >
      <template slot="icon">
        <!--
          NOTE: If the color is not given, the button will look gray, even when it is not disabled.
          Must be set to 'black' in order to look clickable
        -->
        <v-icon
          color="black"
        >
          {{ $vuetify.icons.values.import }}
        </v-icon>
      </template>
    </upload-button>

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

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import UploadButton from 'vuetify-upload-button'

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

function parse (xmlString: string): Document {
  const parser = new DOMParser()
  const parsererrorNS = parser.parseFromString('INVALID', 'text/xml').getElementsByTagName('parsererror')[0].namespaceURI || ''
  const dom = parser.parseFromString(xmlString, 'text/xml')
  return dom.getElementsByTagNameNS(parsererrorNS, 'parsererror').length > 0
    ? new Document() // Should be equivalent to null, or an empty string
    : dom
}

function fileHandler (store: Store, fileName: string): (e: any) => void {
  return (e: any): void => {
    const fileContent = e.target.result
    let json: string | null = null

    store.commit('LOADING', { loading: true, message: `Checking the model file, "${fileName}", for consistency` }, { root: true })
    try {
      json = xml2json(fileContent, { compact: false, ignoreComment: true })
    } catch (err) {
      displayError(
        'The file you tried to open is not valid XML and cannot be used\n'
        + 'Fix the following error before opening again:\n\n'
        + err.message
      )
    }
    if (json) {
      const dom = parse(fileContent)
      rms.isApsModelValid(btoa(unescape(encodeURIComponent(new XMLSerializer().serializeToString(dom)))))
        .then((result: { valid: boolean, error: string }) => {
          if (result.valid) {
            resetState()
            store.commit('LOADING', { loading: true, message: 'Resetting the state...' }, { root: true })
            store.dispatch('fetch')
              .then(() => {
                store.dispatch('modelFileLoader/populateGUI', { json, fileName })
              })
          } else {
            displayError(
              'The file you tried to open is not a valid APS model file and cannot be used\n'
              + 'Fix the following error before opening again:\n\n'
              + result.error
            )
          }
        })
    }
    store.commit('LOADING', { loading: false }, { root: true })
  }
}

@Component({
  components: {
    ExportState,
    ExportDialog,
    JobSettings,
    IconButton,
    UploadButton,
    ChangelogDialog,
    LoadJob,
    RunJob,
  },
})
export default class TheToolBar extends Vue {
  refreshing = false

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

  importModelFile (file: File | null): void {
    if (file) {
      const reader = new FileReader()
      reader.onloadend = fileHandler(this.$store, file.name)
      reader.readAsText(file);
      (this.$refs.uploadButton as UploadButton).clear()
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