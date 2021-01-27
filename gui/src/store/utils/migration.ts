import rms from '@/api/rms'
import { displayMessage } from '@/store/utils'
import { encodeState } from '@/utils'

import { Store } from '@/store/typing'

export default async function migrate (context: Store, state: any, toVersion: string): Promise<any> {
  /* Inspired by: https://typeofnan.dev/an-approach-to-js-object-schema-migration/ */
  const fromVersion = state.version
  if (fromVersion === toVersion) return state

  context.commit('LOADING', { message: `Migrating state from version ${fromVersion} to ${toVersion}` })
  if (!await rms.canMigrate(fromVersion, toVersion)) {
    // Uses "base method" to avoid circular dependencies
    displayMessage(
      context,
      `The stored job uses a format that is no longer supported. We attempt to update it to the current version (${toVersion}).
The migration might not be completely successful. If you experience any issues, consider exporting the model, and then importing the model file into a new job.`,
      'warning',
    )
  }

  try {
    const result = await rms.migrate(encodeState(state), fromVersion, toVersion)
    await context.dispatch('startLoading')
    if (result.errors) {
      displayMessage(
        context,
        result.errors,
        'error',
      )
      return state
    }
    return result.state
  } catch (e) {
    displayMessage(
      context,
      e.message,
      'error',
    )
    console.error(e)
    return state
  }
}
