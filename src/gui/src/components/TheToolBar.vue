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

<script>

import { xml2json } from 'xml-js'
import UploadButton from 'vuetify-upload-button'
import ExportDialog from '@/components/dialogs/ExportDialog'
import ProjectSettings from '@/components/dialogs/ProjectSettings'

import rms from '@/api/rms'
import IconButton from '@/components/selection/IconButton'
import { resetState } from '@/store'

const parse = xmlString => {
  const parser = new DOMParser()
  const parsererrorNS = parser.parseFromString('INVALID', 'text/xml').getElementsByTagName('parsererror')[0].namespaceURI
  const dom = parser.parseFromString(xmlString, 'text/xml')
  return dom.getElementsByTagNameNS(parsererrorNS, 'parsererror').length > 0 ? '' : dom
}

const fileHandler = (store, fileName) => {
  return (e) => {
    const fileContent = e.target.result
    let json = null
    try {
      json = xml2json(fileContent, { compact: true, ignoreComment: true })
    } catch (err) {
      alert('The file you tried to open is not valid XML and cannot be used\n'
        + 'Fix the following error before opening again:\n\n'
        + err.message)
    }
    if (json) {
      const dom = parse(fileContent)
      rms.isApsModelValid(btoa(unescape(encodeURIComponent(new XMLSerializer().serializeToString(dom)))))
        .then(result => {
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

export default {
  components: {
    ExportDialog,
    ProjectSettings,
    IconButton,
    UploadButton
  },

  computed: {
    betaBuild () { return process.env.VUE_APP_BUILD_MODE !== 'stable' },
    versionNumber () { return process.env.VUE_APP_APS_VERSION },
    buildNumber () { return process.env.VUE_APP_BUILD_NUMBER },
    commitHash () { return process.env.VUE_APP_HASH },
    versionInformation () {
      return this.versionNumber && this.buildNumber && this.commitHash
        ? `${this.versionNumber}.${this.buildNumber}-${this.commitHash} (beta)`
        : 'live'
    },
  },

  methods: {
    goToHelp () {
      rms.openWikiHelp()
    },
    importModelFile (file) {
      if (file) {
        const reader = new FileReader()
        reader.onloadend = fileHandler(this.$store, file.name)
        reader.readAsText(file)
        this.$refs.uploadButton.clear()
      }
    },
    exportModelFile: async function () {
      const exportedXMLString = await this.$store.dispatch('modelFileExporter/createModelFileFromStore', {})
        .catch(error => {
          alert(error.message)
        })
      if (exportedXMLString) {
        const result = await rms.isApsModelValid(btoa(exportedXMLString))
        if (result.valid) {
          const defaultPath = `${this.$store.state.parameters.path.project.selected}/myApsExport.xml`
          this.$refs.exportDialog.open(defaultPath, {})
            .then(({ save, path }) => {
              if (save) {
                const resultPromise = rms.save(path, btoa(exportedXMLString))
                resultPromise.then((success) => {
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
  },
}
</script>
