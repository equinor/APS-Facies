import { Optional, Maybe } from '@/utils/typing/simple'

interface HeaderItem {
  text: string
  value?: string
  class?: string
  help?: string
  sortable?: boolean
}

interface ListItem<T> {
  value?: T
  text: string
  disabled?: boolean
  help?: string
}

type HeaderItems = HeaderItem[]

export {
  Optional,
  Maybe,
  HeaderItem,
  HeaderItems,
  ListItem,
}
