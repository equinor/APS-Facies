import { GlobalFacies } from '@/utils/domain'
import CodeError from '@/utils/domain/bases/discrete/codeError'
import { APSTypeError } from '@/utils/domain/errors'
import type { Color } from '@/utils/domain/facies/helpers/colors'

const simpleFaciesDefinition = {
  code: 0,
  color: '#000' as Color,
  name: 'F1',
}

describe('Creating global facies', () => {
  it('Should create a new Facies', () => {
    const facies = new GlobalFacies(simpleFaciesDefinition)
    expect(facies).toBeTruthy()

    expect(facies.code).toBe(0)
    expect(facies.name).toBe('F1')
    expect(facies.color).toBe('#000')
    expect(facies.alias).toBe('F1')
  })

  it('Should not be possible to create one with negative code', () => {
    expect(
      () => new GlobalFacies({ ...simpleFaciesDefinition, code: -1 }),
    ).toThrow(CodeError)
  })

  it('Should not be possible to create one with non-integer code', () => {
    expect(
      () => new GlobalFacies({ ...simpleFaciesDefinition, code: 1.1 }),
    ).toThrow(APSTypeError)
  })
})

describe('When reading from RMS', () => {
  const rmsFacies = [
    { code: 1, name: 'F1', color: '#7cfc00' },
    { code: 2, name: 'F2', color: '#808080' },
    { code: 3, name: 'F3', color: '#1e90ff' },
    { code: 4, name: 'F4', color: '#ffd700' },
    { code: 5, name: 'F5', color: '#9932cc' },
  ] as { code: number, name: string, color: Color }[]
  const facies = rmsFacies.map((spec) => new GlobalFacies(spec))

  it('Should have unique IDs', () => {
    expect(new Set(facies.map(({ id }) => id)).size).toBe(rmsFacies.length)
  })

  it('Should have the same values as from RMS', () => {
    facies.forEach((facies, index) => {
      expect(facies.code).toBe(rmsFacies[index].code)
      expect(facies.name).toBe(rmsFacies[index].name)
      expect(facies.color).toBe(rmsFacies[index].color)
    })
  })
})
