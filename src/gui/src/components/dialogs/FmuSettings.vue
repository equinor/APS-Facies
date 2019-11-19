<template>
  <v-card outlined>
    <v-list-item>
      <v-list-item-title
        class="headline"
      >
        FMU Settings
      </v-list-item-title>
    </v-list-item>
    <v-col class="dense">
      <v-checkbox
        v-model="_runFmuWorkflows"
        label="Run FMU workflows"
      />
    </v-col>
    <div v-if="_runFmuWorkflows">
      <v-row
        no-gutters
      >
        <v-col
          class="pa-2"
          cols="3"
        >
          FMU Parameters List Location
        </v-col>
        <v-col
          class="pa-2"
          cols="5"
        >
          <v-text-field
            v-model="_fmuParameterListLocation"
            single-line
            solo
          />
        </v-col>
        <v-col
          class="pa-2"
          cols="4"
        >
          <bold-button
            title="Select Directory"
            @click="chooseFmuParametersFileLocation"
          />
        </v-col>
      </v-row>
    </div>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import rms from '@/api/rms'

import BoldButton from '@/components/baseComponents/BoldButton.vue'
import NumericField from '@/components/selection/NumericField.vue'

@Component({
  components: {
    NumericField,
    BoldButton,
  }
})
export default class FmuSettings extends Vue {
  @Prop({ required: true })
  readonly fmuParameterListLocation: string

  @Prop({ required: true, type: Boolean })
  readonly runFmuWorkflows: boolean

  get _fmuParameterListLocation (): string { return this.fmuParameterListLocation }
  set _fmuParameterListLocation (path: string) { this.$emit('update:fmuParameterListLocation', path)}

  get _runFmuWorkflows (): boolean { return this.runFmuWorkflows }
  set _runFmuWorkflows (toggled: boolean) { this.$emit('update:runFmuWorkflows', toggled) }

  chooseFmuParametersFileLocation () {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this._fmuParameterListLocation = path
      }
    })
  }
}
</script>
