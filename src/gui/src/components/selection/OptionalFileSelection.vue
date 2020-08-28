<template>
  <v-row>
    <v-col cols="1">
      <v-checkbox
        v-model="enabled"
      />
    </v-col>
    <v-col>
      <file-selection
        v-model="path"
        :label="label"
        :disabled="!enabled"
        @update:error="e => propagateError(e)"
      />
    </v-col>
  </v-row>
</template>
<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import FileSelection from './FileSelection.vue'

interface State {
  path: string
  disabled: boolean
}

@Component({
  components: {
    FileSelection,
  },
})
export default class OptionalFileSelection extends Vue {
  @Prop({ required: true })
  readonly value!: State

  @Prop({ required: true })
  readonly label!: string

  get path (): string {
    return this.value.path
  }

  set path (path: string) {
    this.$emit('input', { ...this.value, path })
  }

  get enabled (): boolean {
    return !this.value.disabled
  }

  set enabled (enabled: boolean) {
    this.$emit('input', { ...this.value, disabled: !enabled })
  }

  propagateError (error: boolean): void {
    this.$emit('update:error', error)
  }
}
</script>
