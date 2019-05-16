<template>
  <v-toolbar>
    <div>
      APS Model:
    </div>

    <v-text-field
      v-model="modelName"
    />

    <!--
      NOTE: the attribute 'flat' has been replaced with 'color=""', as to avoid  mutating a prop directly
      This is *exactly* the same as what's done in the source code for the upload button
    -->
    <upload-button
      ref="uploadButton"
      :file-changed-callback="e => importModelFile(e)"
      color=""
      icon
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
    modelName: {
      get: function () { return this.$store.state.parameters.names.model.selected },
      set: function (value) { this.$store.dispatch('parameters/names/model/select', value, { root: true }) }
    },
  },

  methods: {
    goToHelp () {
      rms.openWikiHelp()
    },
    importModelFile (file) {
      const reader = new FileReader()
      reader.onloadend = fileHandler(this.$store, file.name)
      reader.readAsText(file)
      this.$refs.uploadButton.clear()
    },
    exportModelFile: async function () {
      const exportedXMLString = await this.$store.dispatch('modelFileExporter/createModelFileFromStore', {})
        .catch(error => {
          alert(error.message)
        })
      if (exportedXMLString) {
        const result = await rms.isApsModelValid(btoa(exportedXMLString))
        if (result.valid) {
          const defaultPath = `${this.$store.state.parameters.path.project}/myApsExport.xml`
          this.$refs.exportDialog.open(defaultPath, {})
            .then((result) => {
              if (result.save) {
                const resultPromise = rms.save(result.path, btoa(exportedXMLString))
                resultPromise.then((success) => {
                  if (success) {
                    alert(`model file was saved to ${result.path}`)
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
