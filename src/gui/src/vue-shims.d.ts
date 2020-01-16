declare module '*.vue' {
  import Vue from 'vue'
  export default Vue
}

declare module '*.json' {
  const value: any
  export default value
}

// FIXME: Workaround for Vuetify's 'types' module being "undefined"
declare module 'types' {
  type TouchHandlers = any
  type TouchValue = any
  type TouchWrapper = any
  type DataTableCompareFunction<T> = any
  type SelectItemKey = any

  export {
    TouchHandlers,
    TouchValue,
    TouchWrapper,
    DataTableCompareFunction,
    SelectItemKey,
  }
}
