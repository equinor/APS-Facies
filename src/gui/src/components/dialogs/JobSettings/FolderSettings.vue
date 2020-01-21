<template>
  <SettingsPanel title="Folder Settings">
    <v-row no-gutters>
      <v-col
        class="pa-2"
        cols="3"
      >
        APS Model File Location:
      </v-col>
      <v-col
        class="pa-2"
        cols="5"
      >
        <v-text-field
          v-model="_apsModelFileLocation"
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
          @click="chooseApsModelFileLocation"
        />
      </v-col>
    </v-row>
  </SettingsPanel>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import rms from '@/api/rms'

import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import BoldButton from '@/components/baseComponents/BoldButton.vue'

@Component({
  components: {
    SettingsPanel,
    BoldButton,
  }
})
export default class FolderSettings extends Vue {
  @Prop({ required: true })
  readonly apsModelFileLocation: string

  get _apsModelFileLocation (): string { return this.apsModelFileLocation }
  set _apsModelFileLocation (value: string) { this.$emit('update:apsModelFileLocation', value) }

  chooseApsModelFileLocation (): void {
    rms.chooseDir('load').then((path: string): void => {
      if (path) {
        this._apsModelFileLocation = path
      }
    })
  }
}
</script>
