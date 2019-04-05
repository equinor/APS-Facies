<template>
  <choose-parameter
    :hide-if-disabled="false"
    parameter-type="blockedWellLog"
    label="Blocked well log parameter"
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
