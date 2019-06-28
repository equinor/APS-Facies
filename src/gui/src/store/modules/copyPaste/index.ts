import Vue from 'vue'
import { Parent } from '@/utils/domain/bases/interfaces'
import ZoneRegionDependent, { getParentId } from '@/utils/domain/bases/zoneRegionDependent'
import { APSTypeError } from '@/utils/domain/errors'
import uuidv4 from 'uuid/v4'

import { ID, Identified } from '@/utils/domain/types'
import { Dispatch, Module } from 'vuex'

import { Zone, Region } from '@/utils/domain'

import { RootState } from '@/store/typing'
import CopyPasteState from '@/store/modules/copyPaste/typing'

// eslint-disable-next-line @typescript-eslint/interface-name-prefix
type IDMapping = Map<ID, ID>

interface Element {
  name: string
  items: ZoneRegionDependent[]
  serialization: string
}

function listify (obj: Identified<ZoneRegionDependent>): ZoneRegionDependent[] {
  return Object.values(obj)
}

function getParent (item: Zone | Region): Parent {
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

function copyItems (element: Element, parent: Parent, idMapping: IDMapping): void {
  const items = Object.values(element.items)
    .filter((item): boolean => item.isChildOf(parent))
  items
    .forEach((item): void => {
      idMapping.set(item.id, uuidv4())
    })
  element.serialization = JSON.stringify(items)
}

function getIDMapping (source: Parent, target: Parent): IDMapping {
  const idMapping: IDMapping = new Map<ID, ID>()
  idMapping.set(JSON.stringify(source), JSON.stringify(target))
  return idMapping
}

function giveNewIds (elements: Element[], source: Parent, target: Parent): string {
  const idMapping = getIDMapping(source, target)
  const _serialization = {}
  for (const element of elements) {
    copyItems(element, source, idMapping)
    _serialization[element.name] = JSON.parse(element.serialization)
  }
  let serialization = JSON.stringify(_serialization)
  for (const [ key, value ] of idMapping) {
    const regex = new RegExp(key, 'gi') // Necessary to change _all_ occurrences, instead of just the first
    serialization = serialization.replace(regex, value)
  }
  return serialization
}

async function removeOld ({ dispatch }: { dispatch: Dispatch }, elements: Element[], target: Parent): Promise<void> {
  for (const element of elements) {
    for (const item of element.items.filter((item): boolean => item.isChildOf(target))) {
      await dispatch(`${element.name}/remove`, item, { root: true })
    }
  }
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
        const elements = [
          {
            name: 'gaussianRandomFields/crossSections',
            items: listify(rootState.gaussianRandomFields.crossSections.available),
            serialization: ''
          },
          { name: 'gaussianRandomFields', items: listify(rootState.gaussianRandomFields.fields), serialization: '' },
          { name: 'facies', items: listify(rootState.facies.available), serialization: '' },
          { name: 'facies/groups', items: listify(rootState.facies.groups.available), serialization: '' },
          { name: 'truncationRules', items: listify(rootState.truncationRules.rules), serialization: '' },
        ]
        await removeOld({ dispatch }, elements.concat().reverse(), parent)
        const serialization = giveNewIds(elements, source, parent)
        for (const [ key, items ] of Object.entries(JSON.parse(serialization))) {
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
    PASTING: (state, { source, toggle }: { source: Parent, toggle: boolean }): void => {
      Vue.set(state._pasting, getParentId(source), toggle)
    },
  },

  getters: {
    parent (state): Parent | null {
      return state.source
        ? getParent(state.source)
        : null
    },
    isPasting (state): (parent: Zone | Region | Parent) => boolean {
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
