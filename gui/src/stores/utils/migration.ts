import rms from '@/api/rms'
import type { RootStoreSerialization } from '@/stores'
import { useRootStore } from '@/stores'
import { displayError, displayWarning } from '@/utils/helpers/storeInteraction'
import { encodeState } from '@/utils'

export default async function migrate(
  data: any,
  toVersion: string,
): Promise<RootStoreSerialization> {
  /* Inspired by: https://typeofnan.dev/an-approach-to-js-object-schema-migration/ */
  const fromVersion = data.version
  if (fromVersion === toVersion) return data as RootStoreSerialization

  const rootStore = useRootStore()

  rootStore.startLoading(
    `Migrating state from version ${fromVersion} to ${toVersion}`,
  )
  if (!(await rms.canMigrate(fromVersion, toVersion))) {
    // Uses "base method" to avoid circular dependencies
    displayWarning(
      `The stored job uses a format that is no longer supported. ` +
        `We attempt to update it to the current version (${toVersion}).\n` +
        `The migration might not be completely successful. ` +
        `If you experience any issues, consider exporting the model, ` +
        `and then importing the model file into a new job.`,
    )
  }


  try {
    const result = await rms.migrate(encodeState(data), fromVersion, toVersion)
    rootStore.startLoading()
    if (result.errors) {
      displayError(result.errors)
      return data
    }
    return result.state
  } catch (e) {
    displayError(e instanceof Error ? e.message : String(e))
    console.error(e)
    return data
  }
}
