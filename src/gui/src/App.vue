<template>
  <v-app id="app">
    <v-app-bar
      app
      flat
      color="#fafafa"
    >
      <v-flex column>
        <tool-bar />
        <information-bar />
      </v-flex>
    </v-app-bar>
    <v-content>
      <main-page />
    </v-content>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ToolBar from '@/components/TheToolBar.vue'
import InformationBar from '@/components/TheInformationBar.vue'
import MainPage from '@/pages/MainPage.vue'

@Component({
  components: {
    MainPage,
    ToolBar,
    InformationBar,
  },
})
export default class App extends Vue {
  beforeMount () {
    // Fetch various parameters
    return this.$store.dispatch('fetch')
  }
}
</script>

<style lang="scss" scoped>
  @import 'style/main';

  #app {
    font-family: $font-family;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  h1, h2 {
    font-weight: normal;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }
  li {
    display: inline-block;
    margin: 0 0;
  }
</style>
