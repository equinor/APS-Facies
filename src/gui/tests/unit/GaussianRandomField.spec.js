import { shallowMount } from '@vue/test-utils'
import GaussianRandomField from '@/components/specification/GaussianRandomField/index'

describe('Specify simple Gaussian Field', () => {
  it('renders name when passed', () => {
    const grfId = 'GRF1'
    const wrapper = shallowMount(GaussianRandomField, {
      propsData: { grfId }
    })
    expect(wrapper.text()).toMatch(grfId)
  })
})
