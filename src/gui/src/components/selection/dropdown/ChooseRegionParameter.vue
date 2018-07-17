<template>
  <choose-parameter
    :disabled="disabled"
    parameter-type="region"
    label="Region parameter"
  />
</template>

<script>
import VueTypes from 'vue-types'
import ChooseParameter from '@/components/selection/dropdown/ChooseParameter'

export default {
  components: {
    ChooseParameter
  },

  props: {
    disabled: VueTypes.bool.def(false)
  },
}
</script>

<style scoped>

</style>
