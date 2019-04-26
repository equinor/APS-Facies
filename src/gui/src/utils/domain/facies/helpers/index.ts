import { ID } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'

export function checkFaciesId (facies: any): ID {
  facies = getId(facies)
  if (!facies) throw new Error(`'facies' MUST be a valid ID (uuid). Was ${facies}`)
  return facies
}
