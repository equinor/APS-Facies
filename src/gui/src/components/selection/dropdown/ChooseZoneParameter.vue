<template>
  <choose-parameter
    :disabled="disabled"
    parameter-type="zone"
    label="Zone parameter"
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
