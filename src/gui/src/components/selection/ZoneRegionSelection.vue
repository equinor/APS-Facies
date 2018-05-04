<template>
  <div>
    <SelectionTable
      :headers="getHeaders('Zone')"
      :items="items"
      @selected="updateSelectedZones"
    />
    <v-checkbox
      v-if="selectedZoneHasRegions"
      :label="'Include Regions'"
      v-model="useRegions"
    />
    <SelectionTable
      v-if="useRegions"
      :headers="getHeaders('Region')"
      :items="availableRegions"
      @selected="updateSelectedRegions"
    />
  </div>
</template>

<script>
import SelectionTable from '@/components/SelectionTable'

export default {
  components: {
    SelectionTable
  },

  data () {
    return {
      items: this.availableZones(),
      selectedZones: [],
      useRegions: false,
      selectedRegions: []
    }
  },

  computed: {
    selectedZone () {
      return this.selectedZones.slice(-1).pop()
    },

    availableRegions () {
      if (this.selectedZone && this.selectedZone.regions) {
        return this.selectedZone.regions.map(x => {
          return {...x, selected: false}
        })
      } else {
        return []
      }
    },

    selectedZoneHasRegions () {
      return this.availableRegions.length > 0
    },
  },

  methods: {
    availableZones () {
      return this.$store.state.availableZones.map(x => {
        return {...x, selected: false}
      })
    },

    updateSelectedZones (value) {
      this.selectedZones = value.map(name => this.availableZones().find(item => item.name === name))
    },

    updateSelectedRegions (value) {
      //
    },

    getHeaders (text) {
      return [
        {
          text: text,
          align: 'left',
          sortable: true,
          value: 'name'
        }
      ]
    }
  }
}
</script>

<style scoped>

</style>
