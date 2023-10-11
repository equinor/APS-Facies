import type { VDataTable } from 'vuetify/components'

export type { Optional, Maybe } from '@/utils/typing/simple'

export type VuetifyColumns = Parameters<VDataTable['$slots']['default']>[0]['columns']

export interface HeaderItem {
  text: string
  value?: string
  class?: string
  help?: string
  sortable?: boolean
}

export interface ListItem<T> {
  value?: T
  title: string
  props?: Partial<{
    disabled: boolean
    help: string
  }>
}

export type HeaderItems = HeaderItem[]
