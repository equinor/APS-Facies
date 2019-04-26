<template>
  <v-app id="app">
    <tool-bar />
    <main-page />
  </v-app>
</template>

<script>
import ToolBar from '@/components/TheToolBar'
import MainPage from '@/pages/MainPage'

export default {
  name: 'App',
  components: {
    MainPage,
    ToolBar
  },

  beforeMount () {
    // Fetch various parameters
    return this.$store.dispatch('fetch')
  },
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
