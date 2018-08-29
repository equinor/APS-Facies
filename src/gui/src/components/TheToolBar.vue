<template>
  <v-toolbar>

    <div>APS Model: </div>

    <v-text-field
      id="file_name_input"
      v-model="fileName"
      single-line
    />

    <bold-button
      title="New"
      @click="newModel"
    />

    <file-select v-model="file"/>

    <bold-button
      title="Save Model"
      @click="saveModel"
    />

    <bold-button
      title="Save Model As"
      @click="saveModelAs"
    />

    <bold-button
      title="Load Session"
      @click="loadSession"
    />

    <bold-button
      title="Save Session"
      @click="saveSession"
    />

    <bold-button
      title="Save Session As"
      @click="saveSessionAs"
    />

    <ProjectSettings/>

  </v-toolbar>
</template>

<script>

import FileSelect from '@/components/selection/ImportApsModel'
import ProjectSettings from '@/components/dialogs/ProjectSettings'
import BoldButton from '@/components/baseComponents/BoldButton'
import { notEmpty } from './../utils/index'

export default {
  components: {
    FileSelect,
    ProjectSettings,
    BoldButton,
  },

  data () {
    return {
      file: null
    }
  },

  computed: {
    fileName: {
      get: function () {
        if (notEmpty(this.file)) {
          return this.file.name
        }
        return ''
      },
      set: function (value) {
        this.file = {name: value}
      }
    }
  },

  methods: {
    newModel () {
      if (this.fileName === '') {
        alert('Please enter a name for your model')
      } else {
        alert('new Model function is not implemented')
      }
    },
    saveModel () {
      if (this.fileName === '') {
        alert('Please enter a name for your model')
      } else {
        alert('save model function is not implemented')
      }
    },
    saveModelAs () {
      alert('save model as function is not implemented')
    },
    loadSession () {
      alert('load session function is not implemented')
    },
    saveSession () {
      alert('save session function is not implemented')
    },
    saveSessionAs () {
      alert('save session as function is not implemented')
    },
  },
}
</script>

<style scoped>

</style>
