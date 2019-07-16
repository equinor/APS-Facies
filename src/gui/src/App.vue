<template>
  <v-app id="app">
    <tool-bar />
    <main-page />
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ToolBar from '@/components/TheToolBar.vue'
import MainPage from '@/pages/MainPage.vue'

@Component({
  components: {
    MainPage,
    ToolBar
  },
})
export default class App extends Vue {
  beforeMount () {
    // Fetch various parameters
    return this.$store.dispatch('fetch')
  }
}
</script>

<style lang="stylus" scoped>
  @pretty-blue #2c3e50

  #app
    font-family 'Roboto' 'Avenir', Helvetica, Arial, sans-serif
    -webkit-font-smoothing antialiased
    -moz-osx-font-smoothing grayscale
    text-align center
    color @pretty-blue
    margin-top 60px

  h1, h2
    font-weight normal

  ul
    list-style-type none
    padding 0

  li
    display inline-block
    margin 0 10px
</style>
