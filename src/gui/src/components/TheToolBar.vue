<template>
  <v-toolbar>
    <!--
      NOTE: the attribute 'flat' has been replaced with 'color=""', as to avoid  mutating a prop directly
      This is *exactly* the same as what's done in the source code for the upload button
    -->
    <upload-button
      ref="uploadButton"
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
          {{ $vuetify.icons.import }}
        </v-icon>
      </template>
    </upload-button>

    <icon-button
      icon="export"
      @click="exportModelFile"
    />

    <export-dialog
      ref="exportDialog"
    />

    <v-spacer />

    <export-state
      v-if="isDevelop"
    />

    <project-settings />

    <v-btn
      disabled
      outline
      color="primary"
    >
      Run Settings
    </v-btn>
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
  </v-toolbar>
</template>

<script lang="ts">
import { Store } from '@/store/typing'
import { Component, Vue } from 'vue-property-decorator'

import { xml2json } from 'xml-js'

// @ts-ignore
import UploadButton from 'vuetify-upload-button'

import ExportDialog from '@/components/dialogs/ExportDialog.vue'
import ProjectSettings from '@/components/dialogs/ProjectSettings.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ExportState from '@/components/debugging/exportState.vue'

import rms from '@/api/rms'
import { resetState } from '@/store'

function parse (xmlString: string): Document {
  const parser = new DOMParser()
  const parsererrorNS = parser.parseFromString('INVALID', 'text/xml').getElementsByTagName('parsererror')[0].namespaceURI || ''
  const dom = parser.parseFromString(xmlString, 'text/xml')
  return dom.getElementsByTagNameNS(parsererrorNS, 'parsererror').length > 0
    ? new Document() // Should be equivalent to null, or an empty string
    : dom
}

function fileHandler (store: Store, fileName: string) {
  // @ts-ignore
  return (e) => {
    const fileContent = e.target.result
    let json: string | null = null
    try {
      json = xml2json(fileContent, { compact: false, ignoreComment: true })
    } catch (err) {
      alert('The file you tried to open is not valid XML and cannot be used\n'
        + 'Fix the following error before opening again:\n\n'
        + err.message)
    }
    if (json) {
      const dom = parse(fileContent)
      rms.isApsModelValid(btoa(unescape(encodeURIComponent(new XMLSerializer().serializeToString(dom)))))
        .then((result: { valid: boolean, error: string }) => {
          if (result.valid) {
            resetState()
            store.dispatch('fetch')
              .then(() => {
                store.dispatch('modelFileLoader/populateGUI', { json, fileName })
              })
          } else {
            alert('The file you tried to open is not a valid APS model file and cannot be used\n'
              + 'Fix the following error before opening again:\n\n'
              + result.error)
          }
        })
    }
  }
}

@Component({
  components: {
    ExportState,
    ExportDialog,
    ProjectSettings,
    IconButton,
    UploadButton
  },
})
export default class TheToolBar extends Vue {
  get betaBuild () { return process.env.VUE_APP_BUILD_MODE !== 'stable' }

  get versionNumber () { return process.env.VUE_APP_APS_VERSION }

  get buildNumber () { return process.env.VUE_APP_BUILD_NUMBER }

  get commitHash () { return process.env.VUE_APP_HASH }

  get versionInformation () {
    return this.versionNumber && this.buildNumber && this.commitHash
      ? `${this.versionNumber}.${this.buildNumber}-${this.commitHash} (beta)`
      : 'live'
  }

  get isDevelop () { return process.env.NODE_ENV === 'develop' }

  goToHelp () {
    rms.openWikiHelp()
  }

  importModelFile (file: File | null) {
    if (file) {
      const reader = new FileReader()
      reader.onloadend = fileHandler(this.$store, file.name)
      reader.readAsText(file);
      (this.$refs.uploadButton as UploadButton).clear()
    }
  }

  async exportModelFile () {
    const exportedXMLString = await this.$store.dispatch('modelFileExporter/createModelFileFromStore', {})
      .catch(error => {
        alert(error.message)
      })
    if (exportedXMLString) {
      const result = await rms.isApsModelValid(btoa(exportedXMLString))
      if (result.valid) {
        const defaultPath = `${this.$store.state.parameters.path.project.selected}/myApsExport.xml`;
        // @ts-ignore
        (this.$refs.exportDialog as ExportDialog).open(defaultPath)
          .then(({ save, path }: { save: boolean, path: string }) => {
            if (save) {
              const resultPromise = rms.save(path, btoa(exportedXMLString))
              resultPromise.then((success: boolean): void => {
                if (success) {
                  alert(`model file was saved to ${path}`)
                }
                if (!success) {
                  alert('Saving failed. Did you choose a path that does not exist?')
                }
              })
            }
          })
      } else {
        alert('The model you have defined is not valid and cannot be exported\n'
          + 'Fix the following error before exporting again:\n\n'
          + result.error)
      }
    }
  }
}
</script>
