import { Cubic } from '@/utils/domain'
import { Orientation } from '@/utils/domain/truncationRule/cubic'
import { generateFields, selectedZone } from './helpers'

const zone = selectedZone()
const backgroundFields = generateFields(2, zone)

describe('When creating a cubic truncation rule', () => {
  it('Should be created', () => {
    const rule = new Cubic({ name: '', direction: Orientation.VERTICAL, polygons: [], backgroundFields, zone })
    expect(rule.root).toBe(null)
  })
})
