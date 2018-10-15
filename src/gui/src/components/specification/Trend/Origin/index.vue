<template>
  <div>
    Origin
    <v-layout
      align-center
      justify-center
      row
      fill-height
    >
      <v-flex>
        <origin-x
          :grf-id="grfId"
          :origin-type="originType"
          coordinate-axis="x"
        />
      </v-flex>
      <v-flex>
        <origin-y
          :grf-id="grfId"
          :origin-type="originType"
          coordinate-axis="y"
        />
      </v-flex>
      <v-flex
        v-if="!isEllipticCone"
      >
        <origin-z
          :grf-id="grfId"
          :origin-type="originType"
          coordinate-axis="z"
        />
      </v-flex>
    </v-layout>
    <v-select
      :items="availableOriginTypes"
      v-model="originType"
      label="Origin type"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex'
import VueTypes from 'vue-types'
import OriginCoordinate from './Coordinate'

export default {
  components: {
    originX: OriginCoordinate,
    originY: OriginCoordinate,
    originZ: OriginCoordinate,
  },

  props: {
    grfId: VueTypes.string.isRequired,
  },

  computed: {
    ...mapState({
      availableOriginTypes: state => state.constants.options.origin.available,
    }),
    trend () { return this.$store.state.gaussianRandomFields.fields[this.grfId].trend },
    isEllipticCone () { return this.trend.type === 'ELLIPTIC_CONE' },
    originType: {
      get: function () { return this.trend.origin.type },
      set: function (value) { this.$store.dispatch('gaussianRandomFields/originType', { grfId: this.grfId, value }) }
    },
  },
}
</script>
