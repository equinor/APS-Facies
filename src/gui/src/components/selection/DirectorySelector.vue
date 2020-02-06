<template>
  <v-row
    no-gutters
  >
    <v-col
      class="pa-2"
      cols="3"
    >
      {{ label }}
    </v-col>
    <v-col
      class="pa-2"
      cols="5"
    >
      <v-text-field
        v-model="directory"
        single-line
        solo
      />
    </v-col>
    <v-col
      class="pa-2"
      cols="4"
    >
      <bold-button
        :title="buttonLabel"
        @click="chooseDirectory"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import rms from '@/api/rms'

import BoldButton from '@/components/baseComponents/BoldButton.vue'

@Component({
  components: {
    BoldButton,
  }
})
export default class DirectorySelector extends Vue {
  @Prop({ required: true })
  readonly label!: string

  @Prop({ default: 'Select Directory' })
  readonly buttonLabel!: string

  @Prop({ required: true })
  readonly value!: string

  get directory (): string { return this.value }
  set directory (path: string) { this.$emit('input', path) }

  async chooseDirectory (): Promise<void> {
    const path = await rms.chooseDir('load')
    if (path) {
      this.directory = path
    }
  }
}
</script>
