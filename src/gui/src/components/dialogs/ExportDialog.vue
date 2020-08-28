<template>
  <v-dialog
    v-model="dialog"
    persistent
    max-width="500px"
    @keydown.esc="abort"
    @keydown.enter="choose"
  >
    <v-card>
      <v-card-title>
        <span class="headline">
          {{ `Export the APS model${fmuMode ? ', and FMU settings': ''}` }}
        </span>
      </v-card-title>
      <v-card-text>
        <v-row>
          <file-selection
            v-model="paths.model"
            label="Model file"
          />
        </v-row>
        <div v-if="fmuMode">
          <v-row>
            <optional-file-selection
              v-model="paths.fmuConfig"
              label="FMU configuration"
            />
          </v-row>
          <v-row>
            <optional-file-selection
              v-model="paths.probabilityDistribution"
              label="Probability distribution template"
            />
          </v-row>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="blue darken-1"
          text
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
import normalize from 'path-normalize'

import FileSelection from '@/components/selection/FileSelection.vue'
import OptionalFileSelection from '@/components/selection/OptionalFileSelection.vue'

import { APSError } from '@/utils/domain/errors'

interface Paths {
  model: string
  fmuConfig: string | null
  probabilityDistribution: string | null
}

interface State {
  path: string
  disabled: boolean
}

interface PathsState {
  model: string
  fmuConfig: State
  probabilityDistribution: State
}

@Component({
  components: {
    FileSelection,
    OptionalFileSelection,
  },
})
export default class ExportDialog extends Vue {
  dialog = false
  resolve: ((value: { paths: Paths | null }) => void) | null = null
  reject: ((reason: string) => void) | null = null
  disabled = false
  paths: PathsState = {
    model: '',
    fmuConfig: { path: '', disabled: true },
    probabilityDistribution: { path: '', disabled: true },
  }

  mounted (): void { this.paths = this.defaultPaths }

  get fmuMode (): boolean { return this.$store.getters.fmuMode }

  get defaultPaths (): PathsState {
    const path = this.$store.state.parameters.path
    const projectLocation = path.project.selected
    const fmuConfigLocation = path.fmuParameterListLocation.selected
    const fmuBaseLocation = `${projectLocation}/../..`
    return {
      model: normalize(`${projectLocation}/myApsExport.xml`),
      fmuConfig: {
        path: normalize(`${fmuConfigLocation}/aps.yaml`),
        disabled: false,
      },
      probabilityDistribution: {
        path: normalize(`${fmuBaseLocation}/ert/input/distributions/aps.dist`),
        disabled: false,
      },
    }
  }

  open (): Promise<{ paths: Paths | null }> {
    this.dialog = true
    return new Promise((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
  }

  choose (): void {
    if (!this.resolve) throw new APSError('resolve has not been set')
    if (!this.paths.model) throw new APSError('path has not been set')

    const get = (item: State): string | null => item.disabled ? null : item.path

    const paths: Paths = {
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
}
</script>
