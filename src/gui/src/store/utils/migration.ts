import cmp from 'semver-compare'
import { displayWarning } from '@/utils/helpers/storeInteraction'

interface Migration {
  from: string
  to: string
  up: (state: any) => any
  down?: (state: any) => any
}

const migrations: Migration[] = []

function getMigrations (fromVersion: string, toVersion: string): Migration[] {
  const _migrations = migrations
    .filter(migration => cmp(toVersion, migration.from) === 1 && cmp(fromVersion, migration.to) === 1)
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

export default function migrate (state: any, toVersion: string): any {
  /* Inspired by: https://typeofnan.dev/an-approach-to-js-object-schema-migration/ */
  const fromVersion = state.version
  if (fromVersion === toVersion) return state

  if (!canMigrate(fromVersion, toVersion)) {
    displayWarning(`The stored job could not be migrated, its version (${fromVersion}) might incompatible with the current version (${toVersion}).`)
    return state
  }

  for (const migration of getMigrations(fromVersion, toVersion)) {
    state = migration.up(state)
  }
  return state
}
