<template>
  <v-container column>
    <h4>Alpha selection</h4>
    <v-layout row>
      <alpha-fields
        :value="value"
        :min-channels="3"
      />
    </v-layout>
    <h4>Truncation rule specification</h4>
    <v-layout>
      <v-flex>
        <v-layout>
          <v-flex>
            <polygon-table
              :value="value"
            />
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
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
