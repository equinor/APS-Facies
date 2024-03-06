import { acceptHMRUpdate, defineStore } from 'pinia'
import ColorLibrary, { type ColorLibrarySpecification } from '@/utils/domain/colorLibrary'
import { type Color, colorLibraries } from '@/utils/domain/facies/helpers/colors'
import { computed } from 'vue'
import type { ID } from '@/utils/domain/types'
import { DEFAULT_COLOR_LIBRARY } from '@/config'
import { APSError } from '@/utils/domain/errors'
import type { ListItem } from '@/utils/typing'
import { useCurrentIdentifiedItems } from '@/stores/utils/identified-items'
import { identify } from '@/utils'
import { useGlobalFaciesStore } from '@/stores/facies/global'

type AvailableState = Record<string, ColorLibrary>

function makeMapping(from: ColorLibrary, to: ColorLibrary): Map<Color, Color> {
  return from.colors.reduce((mapping, color, index): Map<Color, Color> => {
    mapping.set(color, to.colors[index % to.colors.length])
    return mapping
  }, new Map())
}

function hasSameValues(first: string[], second: string[]) {
  return (
    first.every((value) => second.includes(value)) &&
    first.length === second.length
  )
}

function hasDifferentColors(
  first: ColorLibrary[],
  second: ColorLibrary[],
): boolean {
  return !hasSameValues(
    first.map((lib) => lib.name),
    second.map((lib) => lib.name),
  )
}

function merge(first: ColorLibrary[], second: ColorLibrary[]): ColorLibrary[] {
  const namedLibraries: AvailableState = {}
  for (const lib of first) {
    namedLibraries[lib.name] = namedLibraries[lib.name] ?? lib
  }
  for (const lib of second) {
    namedLibraries[lib.name] = namedLibraries[lib.name] ?? lib
  }
  return Object.values(namedLibraries)
}

export const useConstantsFaciesColorsStore = defineStore(
  'constants-facies-colors',
  () => {
    const store = useCurrentIdentifiedItems<ColorLibrary>()

    const availableColors = computed(() => store.current.value?.colors ?? [])

    const libraries = computed<ListItem<ColorLibrary>[]>(() =>
      Object.values(store.identifiedAvailable.value).map((library) => ({
        title: library.name,
        value: library,
      })),
    )

    const byCode = computed(() => {
      return (code: number): Color => {
        const colors = availableColors.value
        return colors[code % colors.length]
      }
    })

    function fetch() {
      const libraries = Object.entries(colorLibraries).map(
        ([name, colors]) => new ColorLibrary({ name, colors }),
      )
      store.available.value = libraries

      const defaultLibrary = libraries.find(
        (library): boolean => library.name === DEFAULT_COLOR_LIBRARY,
      )
      if (!defaultLibrary)
        throw new APSError(
          `The default color library, ${DEFAULT_COLOR_LIBRARY}, is not defined`,
        )
      store.currentId.value = defaultLibrary.id
    }

    function populate(newAvailable: ColorLibrarySpecification[], newCurrentId: ID | null) {
      const { available} = store
      const initializedAvailable = newAvailable.map(conf => new ColorLibrary(conf))
      const newIdentifiedAvailable = identify(initializedAvailable)
      const newCurrent = newCurrentId ?
        newIdentifiedAvailable[newCurrentId] ??
        newAvailable.find((lib) => lib.name === DEFAULT_COLOR_LIBRARY)
        : null
      if (available.value.length === 0) {
        fetch()
      } else if (hasDifferentColors(available.value, initializedAvailable)) {
        available.value = merge(available.value, initializedAvailable)
      } else {
        // Ensure we are using the new IDs
        available.value = initializedAvailable
      }
      if (!newCurrent)
        throw new APSError(`The color library called ${newCurrentId} does not exist`)

      store.currentId.value = newCurrent.id
    }

    function set(colorLibrary: ColorLibrary) {
      const previous = store.current.value!
      store.currentId.value = colorLibrary.id

      const faciesGlobalStore = useGlobalFaciesStore()
      faciesGlobalStore.changeColorPalette(makeMapping(previous, colorLibrary))
    }

    return {
      ...store,
      availableColors,
      libraries,
      byCode,
      fetch,
      populate,
      set,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useConstantsFaciesColorsStore, import.meta.hot),
  )
}
