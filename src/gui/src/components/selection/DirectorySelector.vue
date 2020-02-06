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
        :error-messages="errors"
        @click:append-outer="chooseDirectory"
        @input="touch()"
        @blur="touch()"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { required } from 'vuelidate/lib/validators'
import { VuetifyIcon } from 'vuetify/types/services/icons'

import rms from '@/api/rms'

@Component({
  validations () {
    return {
      directory: {
        required,
        async exists (path: string): Promise<boolean> {
          return rms.exists(path)
        }
      }
    }
  },
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

  get errors (): string[] {
    if (!this.$v.directory) return []

    const errors: string[] = []
    if (!this.$v.directory.$dirty) return errors
    !this.$v.directory.required && errors.push('Is required')
    !this.$v.directory.exists && errors.push('Does not exist')
    return errors
  }

  get icon (): VuetifyIcon { return this.$vuetify.icons.values.folderOpen }

  async chooseDirectory (): Promise<void> {
    const path = await rms.chooseDir('load')
    if (path) {
      this.directory = path
    }
  }

  touch (): void { this.$v.directory && this.$v.directory.$touch() }

  mounted (): void {
    if (this.directory) {
      this.touch()
    }
  }
}
</script>
