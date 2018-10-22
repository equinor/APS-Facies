<template>
  <v-layout>
    <v-flex xs10>
      <v-layout column>
        <v-flex>
          <polygon-table/>
        </v-flex>
      </v-layout>
    </v-flex>
    <v-flex xs2>
      <alpha-fields
        :min-channels="3"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import AlphaFields from '@/components/specification/TruncationRule/AlphaFields'
import PolygonTable from '@/components/specification/TruncationRule/Bayfill/PolygonTable'

export default {
  name: 'BayfillSpecification',

  components: {
    AlphaFields,
    PolygonTable,
  },

  computed: {
  },
}
</script>
