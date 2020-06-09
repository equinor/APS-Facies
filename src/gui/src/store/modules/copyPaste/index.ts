import Vue from 'vue'
import { v4 as uuidv4 } from 'uuid'

import { Element, getElements, removeOld } from '@/store/utils/helpers'

import { getParentId } from '@/utils/domain/bases/zoneRegionDependent'
import { APSTypeError } from '@/utils/domain/errors'

import { ID } from '@/utils/domain/types'
import { Module } from 'vuex'
import { Region, Zone } from '@/utils/domain'
import { ParentReference } from '@/utils/domain/bases/interfaces'

import { RootState } from '@/store/typing'
import CopyPasteState from '@/store/modules/copyPaste/typing'

// eslint-disable-next-line @typescript-eslint/interface-name-prefix
type IDMapping = Map<ID, ID>

function getParent (item: Zone | Region): ParentReference {
  if (item instanceof Zone) {
    return {
      zone: item.id,
      region: null
    }
  } else if (item instanceof Region) {
    return {
      zone: item.zone.id,
      region: item.id,
    }
  } else {
    throw new APSTypeError('The given item is not a Zone, nor a Region')
  }
}

function copyItems (element: Element, parent: ParentReference, idMapping: IDMapping): void {
  const items = Object.values(element.items)
    .filter((item): boolean => item.isChildOf(parent))
  items
    .forEach((item): void => {
      idMapping.set(item.id, uuidv4())
    })
  element.serialization = JSON.stringify(items)
}

function getIDMapping (source: ParentReference, target: ParentReference): IDMapping {
  const idMapping: IDMapping = new Map<ID, ID>()
  idMapping.set(JSON.stringify(source), JSON.stringify(target))
  return idMapping
}

function giveNewIds (elements: Element[], source: ParentReference, target: ParentReference): string {
  const idMapping = getIDMapping(source, target)
  const _serialization = {}
  for (const element of elements) {
    copyItems(element, source, idMapping)
    _serialization[element.name] = JSON.parse(element.serialization)
  }
  let serialization = JSON.stringify(_serialization)
  for (const [key, value] of idMapping) {
    const regex = new RegExp(key, 'gi') // Necessary to change _all_ occurrences, instead of just the first
    serialization = serialization.replace(regex, value)
  }
  return serialization
}

const module: Module<CopyPasteState, RootState> = {
  namespaced: true,

  state: {
    source: null,
    _pasting: {},
  },

  actions: {
    copy ({ commit }, source: Zone | Region | null): void {
      commit('SOURCE', source)
    },
    async paste ({ commit, dispatch, getters, rootState }, target: Zone | Region): Promise<void> {
      const parent = getParent(target)

      if (rootState.regions.use && target instanceof Zone) {
        commit('PASTING', { source: parent, toggle: true })
        await Promise.all(target.regions
          .map((region): Promise<void> => dispatch('paste', region))
        )
        commit('PASTING', { source: parent, toggle: false })
      } else {
        const source = getters.parent
        commit('PASTING', { source: parent, toggle: true })
        const elements = getElements({ rootState })

        await removeOld({ dispatch }, elements.concat().reverse(), parent)
        const serialization = giveNewIds(elements, source, parent)
        for (const [key, items] of Object.entries(JSON.parse(serialization))) {
          await Promise.all((items as object[])
            .map((item): Promise<void> => dispatch(`${key}/add`, item, { root: true }))
          )
        }
        commit('PASTING', { source: parent, toggle: false })
      }
    },
  },

  mutations: {
    SOURCE: (state, source): void => {
      state.source = source
    },
    PASTING: (state, { source, toggle }: { source: ParentReference, toggle: boolean }): void => {
      Vue.set(state._pasting, getParentId(source), toggle)
    },
  },

  getters: {
    parent (state): ParentReference | null {
      return state.source
        ? getParent(state.source)
        : null
    },
    isPasting (state): (parent: Zone | Region | ParentReference) => boolean {
      return (parent): boolean => {
        if (parent instanceof Zone || parent instanceof Region) {
          parent = getParent(parent)
        }
        return !!state._pasting[getParentId(parent)]
      }
    }
  },
}

export default module
