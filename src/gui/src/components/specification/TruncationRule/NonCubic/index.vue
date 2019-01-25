<template>
  <v-container>
    <v-layout row>
      <v-flex xs10>
        <polygon-table
          :value="value"
        />
      </v-flex>
      <v-flex xs2>
        <alpha-fields
          :value="value"
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import VueTypes from 'vue-types'

import AlphaFields from '@/components/specification/TruncationRule/AlphaFields'
import PolygonTable from './table'

import { NonCubic } from '@/store/utils/domain'

export default {
  name: 'NonCubicTruncationRule',

  components: {
    AlphaFields,
    PolygonTable,
  },

  props: {
    value: VueTypes.instanceOf(NonCubic),
  },
}
</script>
