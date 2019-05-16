<template>
  <wait-btn
    :title="title"
    :outline="outline"
    color="primary"
    dark
    @click="e => $emit('click', e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import WaitBtn from '@/components/baseComponents/WaitButton.vue'

@Component({
  components: {
    WaitBtn,
  }
})
export default class BoldButton extends Vue {
  @Prop({ required: true })
  readonly title!: string

  @Prop({ default: false })
  readonly outline!: boolean
}
</script>
