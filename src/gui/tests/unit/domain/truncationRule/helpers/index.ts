import GlobalFacies from '@/utils/domain/facies/global'
import { apsColors } from '@/utils/domain/facies/helpers/colors'
import GaussianRandomField from '@/utils/domain/gaussianRandomField'
import { CODE } from '@/utils/domain/types'
import Zone from '@/utils/domain/zone'

export function generateFields (num: number, zone: Zone): GaussianRandomField[] {
  return [...Array(num)]
    .map((_, index) => new GaussianRandomField({ name: `GRF${index + 1}`, channel: index, zone }))
}

export function selectedZone ({ code = 0, name = 'Upper' }: { code?: CODE, name?: string} = {}): Zone {
  return new Zone({ code, name })
}

export function createFacies (num: number): GlobalFacies[] {
  return [...Array(num)]
    .map((_, index) => {
      return { name: `F0${index + 1}`, code: index }
    })
    .map(conf => new GlobalFacies({ ...conf, color: apsColors[conf.code % apsColors.length] }))
}
