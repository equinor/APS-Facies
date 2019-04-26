<template>
  <v-container column>
    <h4>Alpha selection</h4>
    <v-layout row>
      <alpha-fields
        :value="value"
        :min-fields="3"
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

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import AlphaFields from '@/components/specification/TruncationRule/AlphaFields.vue'
import PolygonTable from '@/components/specification/TruncationRule/Bayfill/PolygonTable.vue'

import { Bayfill } from '@/utils/domain'

@Component({
  components: {
    AlphaFields,
    PolygonTable,
  },

})
export default class BayfillSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: Bayfill
}
</script>
