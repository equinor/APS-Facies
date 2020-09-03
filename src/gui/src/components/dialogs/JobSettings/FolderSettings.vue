<template>
  <settings-panel title="Folder Settings">
    <file-selection
      v-model="_apsModelFileLocation"
      label="APS Model File Location"
      directory
    />
  </settings-panel>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import FileSelection from '@/components/selection/FileSelection.vue'

@Component({
  components: {
    FileSelection,
    SettingsPanel,
  }
})
export default class FolderSettings extends Vue {
  @Prop({ required: true })
  readonly apsModelFileLocation: string

  get _apsModelFileLocation (): string { return this.apsModelFileLocation }
  set _apsModelFileLocation (value: string) { this.$emit('update:apsModelFileLocation', value) }
}
</script>
