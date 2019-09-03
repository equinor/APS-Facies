<template>
  <div>
    <v-tooltip
      v-if="hasHelp"
      bottom
    >
      <template v-slot:activator="{ on }">
        <span v-on="on">{{ text }}</span>
      </template>
      <span>
        {{ help }}
      </span>
    </v-tooltip>
    <span v-else>
      {{ text }}
    </span>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { notEmpty } from '@/utils'

interface MaybeHelpText {
  help?: string
}

interface Text extends MaybeHelpText {
  text: string
  [_: string]: any
}

interface Named extends MaybeHelpText {
  name: string
  [_: string]: any
}

@Component
export default class OptionalHelpItem extends Vue {
  @Prop({ required: true })
  readonly value!: Text | Named | string | number

  get text () {
    // @ts-ignore
    return this.value.text || this.value.name || this.value
  }
  get help () {
    // @ts-ignore
    return this.value.help
  }
  get hasHelp () {
    // @ts-ignore
    return notEmpty(this.help)
  }
}
</script>
