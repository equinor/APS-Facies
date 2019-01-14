<template>
  <v-flex>
    <v-flex>
      <v-btn
        icon
        @click="add"
      >
        <v-icon>{{ $vuetify.icons.add }}</v-icon>
      </v-btn>
      <v-btn
        icon
        :disabled="!hasSelected"
        @click="remove"
      >
        <v-icon>{{ $vuetify.icons.remove }}</v-icon>
      </v-btn>
    </v-flex>
    <facies-table :hide-alias="hideAlias" />
  </v-flex>
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
