<template>
  <v-btn
    :disabled="waiting || disabled"
    :dark="dark"
    :flat="flat"
    :color="color"
    @click="e => $emit('click', e)"
  >
    <slot
      v-if="!title"
    />
    <span v-if="!waiting">
      {{ title }}
    </span>
    <span v-else>
      <v-progress-circular indeterminate />
    </span>
  </v-btn>
</template>

<script>
import VueTypes from 'vue-types'
import { AppTypes } from '@/utils/typing'

export default {
  name: 'WaitBtn',

  props: {
    title: VueTypes.string,
    waiting: VueTypes.bool.def(false),
    disabled: VueTypes.bool.def(false),
    flat: VueTypes.bool.def(false),
    dark: VueTypes.bool.def(false),
    color: AppTypes.color.def('primary'),
  },
}
</script>
