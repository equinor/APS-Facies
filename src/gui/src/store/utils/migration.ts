import cmp from 'semver-compare'
import rms from '@/api/rms'
import { displayMessage } from '@/store/utils'

import { Store } from '@/store/typing'

interface Migration {
  from: string
  to: string
  up: (state: any, context: Store) => Promise<any>
  down?: (state: any) => Promise<any>
}

const migrations: Migration[] = [
  {
    from: '1.0.0',
    to: '1.1.0',
    up: async (state): Promise<any> => {
      const { tolerance } = await rms.constants('max_allowed_fraction_of_values_outside_tolerance', 'tolerance')
      state.parameters.maxAllowedFractionOfValuesOutsideTolerance = {}
      state.parameters.maxAllowedFractionOfValuesOutsideTolerance.selected = tolerance
      return state
    },
  },
  {
    from: '1.1.0',
    to: '1.2.0',
    up: async (state): Promise<any> => {
      async function addZoneThicknesses (): Promise<void> {
        const gridModelId = state.gridModels.current
        if (!gridModelId) return state
        const gridModel = state.gridModels.available[gridModelId]
        const zones = (await rms.zones(gridModel.name)).reduce((mapping, zone) => {
          mapping[zone.code] = zone.thickness
          return mapping
        }, ({} as { [code: number]: number }))
        Object.values(state.zones.available).forEach((zone: any) => {
          zone.thickness = zones[zone.code]
        })
      }
      // Add number of zones to gird models
      async function addNumberOfZonesToGrids (): Promise<void> {
        const mapping = (await rms.gridModels()).reduce((mapping, gridModel) => {
          mapping[gridModel.name] = gridModel.zones
          return mapping
        }, ({} as { [name: string]: number }))
        Object.values(state.gridModels.available).forEach((gridModel: any) => {
          gridModel.zones = mapping[gridModel.name]
        })
      }
      await Promise.all([
        addZoneThicknesses(),
        addNumberOfZonesToGrids(),
      ])
      return state
    },
  },
  {
    from: '1.2.0',
    to: '1.3.0',
    up: async (state): Promise<any> => {
      // Add 'observed' to (global) Facies
      Object.values(state.facies.global.available)
        .forEach((facies: any): void => {
          facies.observed = null
        })
      // Add 'touched' to zones, and regions
      // Other entities have this property as well, but it is not used, and will be added where needed by the state
      Object.values(state.zones.available)
        .forEach((zone: any): void => {
          zone.touched = true
          Object.values(zone.regions || []) // May be null
            .forEach((region: any): void => {
              region.touched = true
            })
        })
      return state
    },
  },
  {
    from: '1.3.0',
    to: '1.4.0',
    up: async (state): Promise<any> => {
      const mapping = (await rms.gridModels()).reduce((mapping, gridModel) => {
        mapping[gridModel.name] = gridModel.hasDualIndexSystem
        return mapping
      }, ({} as { [name: string]: boolean }))
      Object.values(state.gridModels.available).forEach((gridModel: any): void => {
        gridModel.hasDualIndexSystem = mapping[gridModel.name]
      })
      return state
    },
  },
  {
    from: '1.4.0',
    to: '1.4.1',
    up: async (state, context): Promise<any> => {
      const ensureNumericCodes = (item: any): void => {
        let code = item.code
        if (typeof code === 'string') {
          try {
            code = Number.parseInt(code, 10)
          } catch (e) {
            displayMessage(context, `The given code, "${code}" could not be parsed as an integer.`, 'warn')
          }
        }
        item.code = code
      }
      Object.values(state.facies.global.available).forEach(ensureNumericCodes)
      Object.values(state.zones.available).forEach((zone: any) => {
        ensureNumericCodes(zone)
        zone.regions && Object.values(zone.regions).forEach(ensureNumericCodes)
      })
      return state
    },
  },
  {
    from: '1.4.1',
    to: '1.5.0',
    up: async (state): Promise<any> => {
      const { tolerance } = await rms.constants('max_allowed_deviation_before_error', 'tolerance')
      state.parameters.toleranceOfProbabilityNormalisation = {
        selected: tolerance,
      }
      return state
    }
  }
]

function getMigrations (fromVersion: string, toVersion: string): Migration[] {
  const _migrations = migrations
    .filter(migration => cmp(toVersion, migration.from) === 1 && cmp(fromVersion, migration.to) === -1)
  return cmp(toVersion, fromVersion) === 1
    ? _migrations
    : _migrations.slice().reverse()
}

function canMigrate (fromVersion: string, toVersion: string): boolean {
  if (!fromVersion) return false
  let version = fromVersion
  for (const migration of getMigrations(fromVersion, toVersion)) {
    if (version === migration.from) {
      version = migration.to
    }
  }
  return version === toVersion
}

export default async function migrate (context: Store, state: any, toVersion: string): Promise<any> {
  /* Inspired by: https://typeofnan.dev/an-approach-to-js-object-schema-migration/ */
  const fromVersion = state.version
  if (fromVersion === toVersion) return state

  if (!canMigrate(fromVersion, toVersion)) {
    // Uses "base method" to avoid circular dependencies
    displayMessage(
      context,
      `The stored job could not be migrated, its version (${fromVersion}) might incompatible with the current version (${toVersion}).`,
      'warning',
    )
    return state
  }

  for (const migration of getMigrations(fromVersion, toVersion)) {
    state = await migration.up(state, context)
    state.version = migration.to
  }
  return state
}
