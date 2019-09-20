<template>
  <v-row
    class="pt-1 pb-1 pr-0 pl-0 ma-0"
    justify="center"
    align="center"
    no-gutters
  >
    <v-col
      v-if="isDevelop"
      cols="12"
    >
      {{ value }}
    </v-col>
    <v-col
      class="ma-0"
      cols="12"
    >
      <v-row
        v-if="imagePath"
        justify="center"
        align="center"
      >
        <v-img
          aspect-ratio="1"
          :style="style"
          :alt="altText"
          :src="imagePath"
          :max-height="size.height"
          :max-width="size.width"
        />
      </v-row>
      <span v-else>{{ value }}</span>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { getDisabledOpacity, isDevelopmentBuild } from '@/utils/helpers/simple'
import { DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE } from '@/config'

@Component({
})
export default class TruncationRulePreview extends Vue {
  @Prop({ required: true })
  readonly value!: string

  @Prop({ required: true })
  readonly type!: string

  @Prop({ default: '' })
  readonly altText!: string

  @Prop({ default: false, type: Boolean })
  readonly disabled!: boolean

  get imagePath (): string {
    try {
      return require(`@/../public/truncation-rules/${this.type}/${this.value}.png`)
    } catch {
      return ''
    }
  }

  get isDevelop () { return isDevelopmentBuild() }

  get size () { return DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE }

  get style () {
    return {
      opacity: getDisabledOpacity(this.disabled)
    }
  }
}
</script>
