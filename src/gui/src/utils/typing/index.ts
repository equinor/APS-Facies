import { Optional, Maybe } from '@/utils/typing/simple'

interface HeaderItem {
  text: string
  value?: string
  class?: string
  help?: string
  sortable?: boolean
}

type HeaderItems = HeaderItem[]

export {
  Optional,
  Maybe,
  HeaderItem,
  HeaderItems,
}
