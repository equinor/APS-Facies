<template>
  <settings-panel title="Folder Settings">
    <directory-selector
      v-model="_apsModelFileLocation"
      label="APS Model File Location"
    />
  </settings-panel>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import SettingsPanel from '@/components/dialogs/JobSettings/SettingsPanel.vue'
import DirectorySelector from '@/components/selection/DirectorySelector.vue'

@Component({
  components: {
    DirectorySelector,
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
