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

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class BasePolygonOrder extends Vue {
  @Prop({ default: true, type: Boolean })
  readonly canIncrease: boolean

  @Prop({ default: true, type: Boolean })
  readonly canDecrease: boolean

  @Prop({ default: true, type: Boolean })
  readonly canRemove: boolean

  @Prop({ default: true, type: Boolean })
  readonly canAdd: boolean
}
</script>
