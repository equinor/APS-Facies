import type { UnwrapRef } from 'vue'
import type { useSelectableChoice } from '@/stores/parameters/utils/selectable-choice'

export interface SelectableSerialization<
  T = string,
  NULLABLE extends boolean = true,
> {
  selected: T | (NULLABLE extends true ? null : T)
}

export interface AvailableOptionSerialization<T> {
  available: T[]
}

export type SelectableOptionSerialization<
  T = string,
  NULLABLE extends true = true,
> = SelectableSerialization<T, NULLABLE> & AvailableOptionSerialization<T>

export function serializeOptionStore<
  STORE extends UnwrapRef<ReturnType<typeof useSelectableChoice<string>>>,
>(store: STORE): SelectableOptionSerialization {
  return {
    available: store.available,
    selected: store.selected,
  }
}
