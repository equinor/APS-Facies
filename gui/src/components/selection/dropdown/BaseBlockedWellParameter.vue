<template>
  <choose-parameter
    :hide-if-disabled="false"
    :parameter-type="parameterType"
    :label="label"
    warn
    :warn-message="warnMessage"
    :warn-even-when-empty="hasFacies"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'

@Component({
  components: {
    ChooseParameter,
  },
})
export default class ChooseBlockedWellLogParameter extends Vue {
  @Prop({ required: true })
  readonly parameterType: string

  @Prop({ required: true })
  readonly label: string

  @Prop({ required: true })
  readonly warnMessage: string

  get hasFacies (): boolean { return this.$store.getters.faciesTable.length > 0 }
}
</script>
