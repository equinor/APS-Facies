<template>
  <v-layout>
    <v-flex xs10>
      <v-layout column>
        <v-flex>
          <polygon-table
            :value="value"
          />
        </v-flex>
      </v-layout>
    </v-flex>
    <v-flex xs2>
      <alpha-fields
        :value="value"
        :min-channels="3"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import VueTypes from 'vue-types'

import AlphaFields from '@/components/specification/TruncationRule/AlphaFields'
import PolygonTable from '@/components/specification/TruncationRule/Bayfill/PolygonTable'

import { Bayfill } from '@/store/utils/domain'

export default {
  name: 'BayfillSpecification',

  components: {
    AlphaFields,
    PolygonTable,
  },

  props: {
    value: VueTypes.instanceOf(Bayfill),
  },

  computed: {
  },
}
</script>
