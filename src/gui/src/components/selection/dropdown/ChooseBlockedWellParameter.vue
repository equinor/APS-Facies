<template>
  <choose-parameter
    :hide-if-disabled="false"
    parameter-type="blockedWell"
    label="Blocked well parameter"
  />
</template>

<script>
import ChooseParameter from '@/components/selection/dropdown/ChooseParameter'

export default {
  components: {
    ChooseParameter
  },
}
</script>
