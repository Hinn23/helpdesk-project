import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Loader from '../components/Loader.vue'

describe('Loader', () => {
  it('renders default text', () => {
    const wrapper = mount(Loader)
    expect(wrapper.text()).toContain('Загрузка...')
  })

  it('renders custom text', () => {
    const wrapper = mount(Loader, { props: { text: 'Подождите...' } })
    expect(wrapper.text()).toContain('Подождите...')
  })
})
