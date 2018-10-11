<template>
  <div>
    <facies-probability-cube
      v-if="hasFacies"
    />
    <gaussian-random-fields/>
  </div>
</template>

<script>
import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube'
export default {
  components: {
    FaciesProbabilityCube,
    GaussianRandomFields
  },

  computed: {
    hasFacies () { return Object.keys(this.$store.state.facies.available).length > 0 }
  },
}
</script>
