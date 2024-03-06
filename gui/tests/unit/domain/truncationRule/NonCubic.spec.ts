import Facies from '@/utils/domain/facies/local'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import NonCubic from '@/utils/domain/truncationRule/nonCubic'
import { identify } from '@/utils/helpers'
import { createFacies, generateFields, selectedZone } from './helpers'

const zone = selectedZone()
const facies = createFacies(3)

const backgroundFields = generateFields(2, zone)

const polygons = identify(
  [
    { angle: 45, facies: 0, fraction: 0.25 },
    { angle: -45, facies: 0, fraction: 0.25 },
    { angle: 120, facies: 0, fraction: 0.25 },
    { angle: -120, facies: 0, fraction: 0.25 },
    { angle: -180, facies: 1, fraction: 1 },
    { angle: 0, facies: 2, fraction: 1 },
  ].map(
    (config, index) =>
      new NonCubicPolygon({
        ...config,
        facies: new Facies({
          facies: facies[config.facies],
          zone,
        }),
        order: index,
      }),
  ),
)

describe('When creating a NonCubic truncation rule, WITHOUT overlay', () => {
  it('Should be created', () => {
    const rule = new NonCubic({ name: '', polygons, zone, backgroundFields })
    expect(rule).toBeTruthy()
  })
})
