<template>
  <choose-bw-parameter
    parameter-type="blockedWellLog"
    label="Blocked well log parameter"
    warn-message="This will remove all facies, and truncation rules."
  />
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ChooseBwParameter from '@/components/selection/dropdown/BaseBlockedWellParameter.vue'

@Component({
  components: {
    ChooseBwParameter,
  },
})
export default class ChooseBlockedWellLogParameter extends Vue {
}
</script>
