<!--
  The standard button of the redesign. Only its styling is added here;
  everything else, such as 'block', 'loading', and '@click', falls through
  to 'v-btn'. Once every component has been redesigned, this styling can be
  moved to 'defaults' in the Vuetify plugin, and this wrapper removed
-->
<template>
  <v-btn
    variant="outlined"
    color="accent"
    rounded="lg"
    class="action-button text-none font-weight-bold"
  >
    <slot />
  </v-btn>
</template>

<style lang="scss" scoped>
.action-button {
  --v-hover-opacity: 0.16;
}
</style>
