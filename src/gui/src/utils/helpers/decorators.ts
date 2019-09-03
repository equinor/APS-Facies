import { createDecorator } from 'vue-class-component'

// Taken from https://github.com/vuejs/vue-class-component#create-custom-decorators
export const NoCache = createDecorator((options, key): void => {
  // component options should be passed to the callback
  // and update for the options object affect the component

  // @ts-ignore
  options.computed[`${key}`].cache = false
})
