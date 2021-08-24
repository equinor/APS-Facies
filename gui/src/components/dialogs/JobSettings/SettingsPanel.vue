<template>
  <v-card outlined>
    <v-list-item>
      <v-list-item-title
        class="text-h5"
      >
        {{ title }}
      </v-list-item-title>
    </v-list-item>
    <slot />
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class SettingsPanel extends Vue {
  @Prop({ required: true })
  readonly title: string
}
</script>
