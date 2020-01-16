import cmp from 'semver-compare'
import rms from '@/api/rms'
import { displayWarning } from '@/utils/helpers/storeInteraction'

interface Migration {
  from: string
  to: string
  up: (state: any) => Promise<any>
  down?: (state: any) => Promise<any>
}

const migrations: Migration[] = [
  {
    from: '1.0.0',
    to: '1.1.0',
    up: async (state) => {
      const { tolerance } = await rms.constants('max_allowed_fraction_of_values_outside_tolerance', 'tolerance')
      state.parameters.maxAllowedFractionOfValuesOutsideTolerance = {}
      state.parameters.maxAllowedFractionOfValuesOutsideTolerance.selected = tolerance
      return state
    },
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

export default async function migrate (state: any, toVersion: string): Promise<any> {
  /* Inspired by: https://typeofnan.dev/an-approach-to-js-object-schema-migration/ */
  const fromVersion = state.version
  if (fromVersion === toVersion) return state

  if (!canMigrate(fromVersion, toVersion)) {
    displayWarning(`The stored job could not be migrated, its version (${fromVersion}) might incompatible with the current version (${toVersion}).`)
    return state
  }

  for (const migration of getMigrations(fromVersion, toVersion)) {
    state = await migration.up(state)
    state.from = migration.to
  }
  return state
}
