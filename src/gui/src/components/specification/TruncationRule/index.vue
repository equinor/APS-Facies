<template>
  <v-expansion-panel
    :value="0"
  >
    <v-expansion-panel-content>
      <div slot="header">
        <h2>Truncation Rules</h2>
      </div>
      <v-layout row>
        <v-flex xs5>
          <v-select
            v-model="templateName"
            :items="['Cubic', 'Non-cubic', 'Bayfill']"
            label="Rule"
          />
        </v-flex>
        <v-flex xs5>
          <v-combobox
            v-model="truncationType"
            :items="templates"
            label="Template"
          />
        </v-flex>
        <icon-button
          icon="add_box"
          @click="addTemplate"
        />
        <icon-button
          icon="content_copy"
          @click="copyTemplate"
        />
        <icon-button
          icon="delete_forever"
          @click="deleteTemplate"
        />
      </v-layout>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import IconButton from '@/components/selection/IconButton'

export default {
  components: {
    IconButton,
  },

  data () {
    return {
      templateName: '',
      truncationType: '',
    }
  },

  computed: {
    templates () {
      return ['Simple', 'Advanced']
    }
  },

  methods: {
    addTemplate () {},
    copyTemplate () {},
    deleteTemplate () {},
  },
}
</script>

<style scoped>

</style>
