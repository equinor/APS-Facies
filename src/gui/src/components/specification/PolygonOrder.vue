<template>
  <v-layout
    row
    wrap
  >
    <v-flex
      xs6
      column
    >
      <v-icon
        :disabled="!canDecrease"
        small
        @click="() => $emit('input', -1)"
        v-text="'$vuetify.icons.up'"
      />
      <v-icon
        :disabled="!canIncrease"
        small
        @click="() => $emit('input', +1)"
        v-text="'$vuetify.icons.down'"
      />
    </v-flex>
    <v-flex
      xs6
      column
    >
      <v-icon
        :diabled="!canRemove"
        small
        @click="() => $emit('delete')"
        v-text="'$vuetify.icons.remove'"
      />
      <v-icon
        :disabled="!canAdd"
        small
        @click="() => $emit('add')"
        v-text="'$vuetify.icons.add'"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import VueTypes from 'vue-types'

export default {
  name: 'PolygonOrder',

  props: {
    canIncrease: VueTypes.bool.def(true),
    canDecrease: VueTypes.bool.def(true),
    canRemove: VueTypes.bool.def(true),
    canAdd: VueTypes.bool.def(true),
  },
}
</script>
