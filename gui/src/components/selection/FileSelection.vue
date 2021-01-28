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
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { required } from 'vuelidate/lib/validators'

import rms from '@/api/rms'
import { relativeTo } from '@/utils/queries'

@Component({
  validations () {
    // eslint-disable-next-line no-use-before-define
    const checkFileDirectory = (this as FileSelection).file
    return {
      path: {
        required,
        async exists (path: string): Promise<boolean> {
          return rms.exists(btoa(path), checkFileDirectory)
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

  @Prop({ default: undefined })
  readonly relativeTo!: string | undefined

  get path (): string | null {
    if (this.relativeTo && this.value) return relativeTo(this.relativeTo, this.value)
    return this.value
  }

  set path (value: string | null) {
    if (this.relativeTo && !value?.startsWith('/')) {
      value = `${this.relativeTo}/${value}`
    }
    this.$emit('input', value)
  }

  get errors (): string[] {
    if (!this.$v.path) return []

    const errors: string[] = []
    if (!this.$v.path.$dirty) return errors
    !this.$v.path.required && errors.push('Is required')
    !this.$v.path.exists && errors.push('Directory does not exist')
    return errors
  }

  get icon (): string { return `$vuetify.icons.values.${this.open ? 'openFolder' : 'folder'}` }

  get file (): boolean { return !this.directory }

  async choosePath (): Promise<void> {
    this.open = true
    let path = null
    try {
      path = this.directory
        ? await rms.chooseDir('load')
        // setting parameters filter and suggestion does not seem to work...
        : await rms.chooseFile('save', '', '')
    } catch {}
    if (path) {
      this.path = path
    }
    this.open = false
  }

  touch (): void { this.$v.path && this.$v.path.$touch() }

  mounted (): void {
    if (this.path) {
      this.touch()
      this.$emit('update:error', this.$v.$invalid)
    }
  }

  @Watch('$v.$invalid')
  onInvalidChanged (invalid: boolean): void {
    this.$emit('update:error', invalid)
  }
}

</script>
