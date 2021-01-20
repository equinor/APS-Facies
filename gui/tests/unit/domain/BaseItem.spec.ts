import BaseItem from '@/utils/domain/bases/baseItem'
import { v4 as uuid } from 'uuid'

describe('Creating a new BaseItem', () => {
  it('Should be created', () => {
    const item: BaseItem = new BaseItem()
    expect(item).toBeTruthy()
  })

  it('Should what the same ID, if one is given', () => {
    const id = uuid()
    const item = new BaseItem({ id })
    expect(item.id).toBe(id)
  })

  it('Should not be possible to give a non-UUID string as input', () => {
    const makeInvalidItem = (): BaseItem => new BaseItem({ id: 'not an UUID' })
    expect(makeInvalidItem).toThrow(TypeError)
  })
})
