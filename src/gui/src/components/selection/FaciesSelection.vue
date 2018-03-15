<template>
  <v-container>
    <v-data-table
      :headers="headers"
      :items="items"
      class="elevation-1"
    >
      <template
        slot="items"
        slot-scope="props"
      >
        <td class="text-xs-right">{{ props.item.name }}</td>
        <td class="text-xs-right">{{ props.item.code }}</td>
        <td class="text-xs-right"><Swatches v-model="props.item.color"/></td>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import ItemTable from '@/components/ItemTable'
import Swatches from 'vue-swatches'

export default {
  components: {
    ItemTable,
    Swatches
  },

  data () {
    return {
      headers: [
        {text: 'Facies', value: 'name'},
        {text: 'Code', value: 'code'},
        {text: 'Color', value: 'color'}
      ],
      items: this.availableFacies()
    }
  },

  methods: {
    availableFacies () {
      return this.$store.state.availableFacies.map(item => {
        return {...item, value: false}
      })
    }
  }
}
</script>

<style scoped>

</style>
