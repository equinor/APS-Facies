<template>
  <v-responsive
    class="overflow-y-auto"
    :max-height="height"
    @resize="updateHeight"
  >
    <slot
      ref="component"
    />
  </v-responsive>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({
})
export default class ScrollableArea extends Vue {
  height = 0

  @Prop({ default: 64 }) // 64 is the height of the toolbar
  readonly offset!: number

  mounted (): void {
    this.updateHeight()
    // Necessary, in order to listen to when RMS' console changes size
    addEventListener('resize', this.updateHeight)
  }

  updateHeight (): void {
    const component = (this.$refs.component as Vue | undefined)
    this.height = (component ? component.$el.clientHeight : window.innerHeight) - this.offset
  }

  destroy (): void {
    removeEventListener('resize', this.updateHeight)
  }
}
</script>
