import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

describe('When making an FMU-updatable value', () => {
  it('Should have the same value as was passed', () => {
    const value = 500
    const fmuValue = new FmuUpdatableValue(value)
    expect(fmuValue.value).toBe(value)
  })

  it("Should have a default value of 'non-updatable', when none is given", () => {
    const value = new FmuUpdatableValue(0)
    expect(value.updatable).toBe(false)
  })

  it('Should contain the same values as where passed', () => {
    const value = 200
    const updatable = true

    const fmuValue = new FmuUpdatableValue(value, updatable)
    expect(fmuValue.value).toBe(value)
    expect(fmuValue.updatable).toBe(updatable)
  })

  it('Should be possible to create an FMU-updatable value from an object', () => {
    const value = {
      updatable: true,
      value: 400,
    }

    const fmuValue = new FmuUpdatableValue(value)
    expect(fmuValue.value).toBe(value.value)
    expect(fmuValue.updatable).toBe(value.updatable)
  })

  it('The updatability on a passed object should have precedent over the given updatable value', () => {
    const value = {
      updatable: true,
      value: 0,
    }
    const updatable = !value.updatable
    const fmuValue = new FmuUpdatableValue(value, updatable)
    expect(fmuValue.updatable).not.toBe(updatable)
  })
})
