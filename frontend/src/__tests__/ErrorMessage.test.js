import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorMessage from '../components/ErrorMessage.vue'

describe('ErrorMessage', () => {
  it('renders message when provided', () => {
    const wrapper = mount(ErrorMessage, { props: { message: 'Ошибка' } })
    expect(wrapper.text()).toContain('Ошибка')
  })

  it('does not render when message is empty', () => {
    const wrapper = mount(ErrorMessage, { props: { message: '' } })
    expect(wrapper.find('.error-box').exists()).toBe(false)
  })
})
