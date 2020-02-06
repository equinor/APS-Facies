<template>
  <v-row
    no-gutters
  >
    <v-col
      class="pa-2"
      cols="12"
    >
      <v-text-field
        v-model="directory"
        :label="label"
        :append-outer-icon="icon"
        @click:append-outer="chooseDirectory"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { VuetifyIcon } from 'vuetify/types/services/icons'

import rms from '@/api/rms'

@Component({
  components: {
  }
})
export default class DirectorySelector extends Vue {
  @Prop({ required: true })
  readonly label!: string

  @Prop({ required: true })
  readonly value!: string

  get directory (): string { return this.value }
  set directory (path: string) { this.$emit('input', path) }

  get icon (): VuetifyIcon { return this.$vuetify.icons.values.folderOpen }

  async chooseDirectory (): Promise<void> {
    const path = await rms.chooseDir('load')
    if (path) {
      this.directory = path
    }
  }
}
</script>
