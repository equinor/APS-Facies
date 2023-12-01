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
      cols="12"
    >
      <v-row
        justify="center"
        align="center"
      >
        <v-img
          aspect-ratio="1"
          eager
          :style="style"
          :alt="altText"
          :src="imagePath"
          :max-height="size.height"
          :max-width="size.width"
        />
      </v-row>
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
    // eslint-disable-next-line security/detect-non-literal-require
    return require(`@/../public/truncation-rules/${this.type}/${this.value}.svg`)
  }

  get isDevelop (): boolean { return isDevelopmentBuild() }

  get size (): { width: number, height: number } { return DEFAULT_TRUNCATION_RULE_TEMPLATE_PREVIEW_SIZE }

  get style (): { opacity: number } {
    return {
      opacity: getDisabledOpacity(this.disabled)
    }
  }
}
</script>
