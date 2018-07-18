<template>
  <choose-parameter
    :disabled="disabled"
    parameter-type="region"
    label="Region parameter"
  />
</template>

<script>
import VueTypes from 'vue-types'
import ChooseParameter from 'Components/selection/dropdown/ChooseParameter'

export default {
  components: {
    ChooseParameter
  },

  props: {
    disabled: VueTypes.bool.def(false)
  },
}
</script>
