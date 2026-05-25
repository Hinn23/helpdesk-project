import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../components/BaseButton.vue'

describe('BaseButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'Нажми меня' } })
    expect(wrapper.text()).toContain('Нажми меня')
  })

  it('applies primary variant by default', () => {
    const wrapper = mount(BaseButton)
    expect(wrapper.classes()).toContain('btn-primary')
  })

  it('applies danger variant', () => {
    const wrapper = mount(BaseButton, { props: { variant: 'danger' } })
    expect(wrapper.classes()).toContain('btn-danger')
  })

  it('disables button', () => {
    const wrapper = mount(BaseButton, { props: { disabled: true } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('applies sm size class', () => {
    const wrapper = mount(BaseButton, { props: { size: 'sm' } })
    expect(wrapper.classes()).toContain('btn-sm')
  })
})
