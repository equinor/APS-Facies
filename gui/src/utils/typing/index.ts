import type { VDataTable } from 'vuetify/components'

export type { Optional, Maybe } from '@/utils/typing/simple'

export type VuetifyColumns = Parameters<VDataTable['$slots']['default']>[0]['columns']

export interface HeaderItem {
  text: string
  value?: string
  class?: string
  headerProps?: {
    help?: string
  }
  sortable?: boolean
}

export interface ListItem<T, AdditionalProps extends object = Record<string, unknown>> {
  value?: T
  title: string
  props?: Partial<{
    disabled: boolean
    help: string
  }> & AdditionalProps
}

export type HeaderItems = HeaderItem[]
