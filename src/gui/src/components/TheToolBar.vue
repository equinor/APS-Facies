<template>
  <v-toolbar>

    <div>
      APS Model:
    </div>

    <v-text-field
      v-model="modelName"
    />

    <upload-button
      :file-changed-callback="e => importModelFile(e)"
      title="Import"
    />

    <bold-button
      title="Export"
      disabled="true"
    />

    <v-spacer/>

    <ProjectSettings/>

    <bold-button
      title="Run Settings"
      diabled="true"
    />

  </v-toolbar>
</template>

<script>

import { xml2json } from 'xml-js'
import UploadButton from 'vuetify-upload-button'

import ProjectSettings from '@/components/dialogs/ProjectSettings'
import BoldButton from '@/components/baseComponents/BoldButton'

import rms from '@/api/rms'

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
      console.log(err)
      alert('The file you tried to open is not valid XML and cannot be used\n' +
        'Fix the following error before opening again:\n\n' +
        err.message)
    }
    if (json) {
      const dom = parse(fileContent)
      rms.isApsModelValid(btoa(new XMLSerializer().serializeToString(dom)))
        .then(result => {
          if (result.valid) {
            store.dispatch('modelFileLoader/populateGUI', { json, fileName })
          } else {
            alert('The file you tried to open is not a valid APS model file and cannot be used\n' +
              'Fix the following error before opening again:\n\n' +
              result.error)
          }
        })
    }
  }
}

export default {
  components: {
    ProjectSettings,
    BoldButton,
    UploadButton
  },

  data () {
    return {}
  },

  computed: {
    modelName: {
      get: function () { return this.$store.state.modelName.selected },
      set: function (value) { this.$store.dispatch('modelName/select', value, { root: true }) }
    },
  },

  methods: {
    importModelFile (file) {
      const reader = new FileReader()
      reader.onloadend = fileHandler(this.$store, file.name)
      reader.readAsText(file)
    },
  },
}
</script>

<style scoped>

</style>
