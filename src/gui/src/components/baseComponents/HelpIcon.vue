<template>
  <v-popover
    trigger="hover"
  >
    <v-icon
      :color="color"
    >
      {{ $vuetify.icons.help }}
    </v-icon>
    <span slot="popover">
      <slot />
    </span>
  </v-popover>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { Color } from '@/utils/domain/facies/helpers/colors'

@Component
export default class HelpIcon extends Vue {
  @Prop({ default: 'black' })
  readonly color: Color
}
</script>
