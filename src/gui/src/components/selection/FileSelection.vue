<template>
  <v-row
    no-gutters
  >
    <v-col
      class="pa-2"
      cols="12"
    >
      <v-textarea
        v-model="path"
        auto-grow
        rows="1"
        :disabled="disabled"
        :label="label"
        :append-outer-icon="icon"
        :error-messages="errors"
        @keydown.enter.prevent="() => {/* Intentionally ignore 'newline'*/}"
        @click:append-outer="choosePath"
        @input="touch()"
        @blur="touch()"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { required } from 'vuelidate/lib/validators'

import rms from '@/api/rms'

@Component({
  validations () {
    return {
      path: {
        required,
        async exists (path: string): Promise<boolean> {
          return rms.exists(path)
        },
      },
    }
  },
  components: {
  },
})
export default class FileSelection extends Vue {
  private open = false

  @Prop({ required: true })
  readonly value!: string | null

  @Prop({ default: false, type: Boolean })
  readonly disabled!: boolean

  @Prop({ required: true })
  readonly label!: string

  @Prop({ default: false, type: Boolean })
  readonly directory!: boolean

  get path (): string | null { return this.value }
  set path (value: string | null) { this.$emit('input', value) }

  get errors (): string[] {
    if (!this.$v.path) return []

    const errors: string[] = []
    if (!this.$v.path.$dirty) return errors
    !this.$v.path.required && errors.push('Is required')
    !this.$v.path.exists && errors.push('Directory does not exist')
    return errors
  }

  get icon (): string { return `$vuetify.icons.values.${this.open ? 'openFolder' : 'folder'}` }

  async choosePath (): Promise<void> {
    this.open = true
    let path = this.path
    try {
      path = this.directory
        ? await rms.chooseDir('load')
        // setting parameters filter and suggestion does not seem to work...
        : await rms.chooseFile('save', '', '')
    } catch {}
    this.path = path
    this.open = false
  }

  touch (): void { this.$v.path && this.$v.path.$touch() }

  mounted (): void {
    if (this.path) {
      this.touch()
    }
  }
}

</script>
