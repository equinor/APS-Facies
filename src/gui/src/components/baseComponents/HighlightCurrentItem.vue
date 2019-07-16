<template>
  <span :class="item.current ? 'font-weight-bold' : ''">
    {{ item[field] }}
  </span>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class HighlightCurrentItem extends Vue {
  @Prop({ required: true })
  readonly item!: {
    current: boolean
    [_: string]: any
  }

  @Prop({ required: true })
  readonly field!: string
}
</script>
