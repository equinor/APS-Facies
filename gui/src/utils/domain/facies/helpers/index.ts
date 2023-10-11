import Facies from '@/utils/domain/facies/local'
import { ID } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'

export function checkFaciesId(facies: Facies): ID {
  const id = getId(facies)
  if (!id) throw new Error(`'facies' MUST be a valid ID (uuid). Was ${id}`)
  return id
}
