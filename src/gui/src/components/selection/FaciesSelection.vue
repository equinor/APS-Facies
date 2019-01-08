<template>
  <div>
    <facies-table :hide-alias="hideAlias" />
    <div>
      <v-btn
        outline
        color="info"
        @click="add"
      >
        Add Facies
      </v-btn>
      <v-btn
        outline
        :disabled="!hasSelected"
        color="error"
        @click="remove"
      >
        Remove Facies
      </v-btn>
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
      hasSelected: state => !!state.facies.global.current,
    }),
  },

  methods: {
    add () {
      return this.$store.dispatch('facies/global/new', {})
    },
    remove () {
      return this.$store.dispatch('facies/global/removeSelectedFacies')
    },
  }
}
</script>
