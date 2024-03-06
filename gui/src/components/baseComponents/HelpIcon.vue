<template>
  <floating-tooltip trigger="hover">
    <v-icon :color="color">
      {{ vuetify.icons.aliases.help }}
    </v-icon>
    <template #popper>
      <slot />
    </template>
  </floating-tooltip>
</template>

<script setup lang="ts">
import type { Color } from '@/utils/domain/facies/helpers/colors'
import vuetify from '@/plugins/vuetify'
type Props = {
  color?: Color
}
withDefaults(defineProps<Props>(), {
  color: 'black',
})
</script>
