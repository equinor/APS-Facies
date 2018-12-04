<template>
  <v-btn
    :disabled="disabled || waiting"
    :color="color"
    :dark="dark"
    :large="large"
    :left="left"
    :light="light"
    :right="right"
    :small="small"
    icon
    flat
    @click.stop="e => $emit('click', e)"
  >
    <v-icon
      :color="color"
      :dark="dark"
      :large="large"
      :left="left"
      :light="light"
      :medium="medium"
      :right="right"
      :size="size"
      :small="small"
      :x-large="xLarge"
      v-text="fullIconName"
    />
  </v-btn>
</template>

<script>
import VueTypes from 'vue-types'

export default {
  props: {
    icon: VueTypes.string.isRequired,
    waiting: VueTypes.bool.def(false),
    disabled: VueTypes.bool.def(false),
    color: VueTypes.oneOfType([VueTypes.string, undefined]).def(undefined),
    dark: VueTypes.bool.def(false),
    large: VueTypes.bool.def(false),
    left: VueTypes.bool.def(false),
    light: VueTypes.bool.def(false),
    medium: VueTypes.bool.def(false),
    right: VueTypes.bool.def(false),
    size: VueTypes.oneOfType([VueTypes.number, VueTypes.string, undefined]).def(undefined),
    small: VueTypes.bool.def(false),
    xLarge: VueTypes.bool.def(false),
  },

  computed: {
    fullIconName () {
      return `$vuetify.icons.${this.icon}${this.waiting ? 'Spinner' : ''}`
    }
  },
}
</script>

<style scoped>

</style>
