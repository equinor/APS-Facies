import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import GlobalFacies from '@/utils/domain/facies/global'
import Facies from '@/utils/domain/facies/local'
import BayfillPolygon, { type SlantFactorArgs } from '@/utils/domain/polygon/bayfill'
import Bayfill from '@/utils/domain/truncationRule/bayfill'
import { identify } from '@/utils/helpers'
import { createFacies, generateFields, selectedZone } from './helpers'

const zone = selectedZone({ code: 0, name: 'Upper', thickness: 12 })

const facies = createFacies(5)

const polygons = identify(
  ([
    { name: 'Floodplain', slantFactor: 0.5 },
    { name: 'Subbay', slantFactor: 0.5 },
    { name: 'Wave influenced Bayfill' },
    { name: 'Bayhead Delta', slantFactor: 0.5 },
    { name: 'Lagoon' },
  ] as SlantFactorArgs[]).map(
    (config, index) =>
      new BayfillPolygon({
        ...config,
        facies: new Facies({ facies: facies[index], zone }),
        order: index,
      }),
  ),
)

const backgroundFields = generateFields(3, zone)

describe('When setting up required dependencies of a (Bayfill) truncation rule', () => {
  it('Should have one zone', () => {
    expect(zone).toBeTruthy()
    expect(zone.code).toBe(0)
    expect(zone.name).toBe('Upper')
  })

  it('Should have 5 global facies', () => {
    expect(facies.length).toBe(5)
    facies.forEach((facies) => {
      expect(facies instanceof GlobalFacies).toBeTruthy()
    })
  })

  it('Should have 5 polygons', () => {
    expect(Object.values(polygons).length).toBe(5)
  })

  it('Should have distinct (local) facies associated with the polygons', () => {
    Object.values(polygons).forEach((polygon) => {
      expect(polygon.facies instanceof Facies).toBeTruthy()
    })

    const uniqueFacies = new Set(
      Object.values(polygons).map(
        ({ facies }) => (facies as Facies).id || facies,
      ),
    )
    expect(uniqueFacies.size).toBe(5)
  })
})

describe('While creating a Bayfill truncation rule', () => {
  it('Should be initialized', () => {
    const rule = new Bayfill({ name: '', polygons, zone, backgroundFields })
    expect(rule).toBeTruthy()
  })

  it('Should have the required number of components', () => {
    const rule = new Bayfill({ name: '', polygons, zone, backgroundFields })

    expect(rule.polygons.length).toBe(5)
    expect(rule.fields.length).toBe(3)
    expect(rule.specification).toEqual({
      polygons: [
        {
          facies: 'F01',
          factor: new FmuUpdatableValue(0.5, false),
          fraction: 1,
          name: 'SF',
          order: 0,
          polygon: 'Floodplain',
        },
        {
          facies: 'F02',
          factor: new FmuUpdatableValue(0.5, false),
          fraction: 1,
          name: 'YSF',
          order: 1,
          polygon: 'Subbay',
        },
        {
          facies: 'F04',
          factor: new FmuUpdatableValue(0.5, false),
          fraction: 1,
          name: 'SBHD',
          order: 3,
          polygon: 'Bayhead Delta',
        },
      ],
    })
  })
})
