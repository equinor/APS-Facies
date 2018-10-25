<template>
  <div>
    <facies-table :hide-alias="hideAlias"/>
    <div>
      <v-btn
        color="info"
        @click="add"
      >Add Facies</v-btn>
      <v-btn
        :disabled="!hasSelected"
        color="warning"
        @click="remove"
      >Remove Facies</v-btn>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import FaciesTable from '@/components/table/FaciesTable'

export default {
  components: {
    FaciesTable,
  },

  data () {
    return {
      hideAlias: false
    }
  },

  computed: {
    ...mapState({
      available: state => state.facies.available,
      colors: state => state.constants.faciesColors.available,
      hasSelected: state => !!state.facies.current,
    }),
  },

  methods: {
    add () {
      return this.$store.dispatch('facies/new', {})
    },
    remove () {
      return this.$store.dispatch('facies/removeSelectedFacies')
    },
  }
}
</script>
