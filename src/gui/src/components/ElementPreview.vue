<template>
  <div>
    <h1>Preview</h1>
    <truncation-map
      :truncation-rule-id="ruleId"
    />
  </div>
</template>

<script>
import TruncationMap from '@/components/plot/TruncationMap'

export default {
  components: {
    TruncationMap,
  },

  computed: {
    ruleId () {
      const rule = this.$store.getters.truncationRule
      return rule ? rule.id : ''
    }
  },
}
</script>
