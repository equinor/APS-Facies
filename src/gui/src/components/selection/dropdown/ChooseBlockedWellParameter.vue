<template>
  <choose-parameter
    :hide-if-disabled="false"
    parameter-type="blockedWell"
    label="Blocked well parameter"
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'

@Component({
  components: {
    ChooseParameter
  },
})
export default class ChooseBlockedWellParameter extends Vue {
}
</script>
