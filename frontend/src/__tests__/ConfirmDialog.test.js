import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfirmDialog from '../components/ConfirmDialog.vue'

describe('ConfirmDialog', () => {
  function mountDialog(props = {}) {
    return mount(ConfirmDialog, {
      props: { visible: true, ...props },
      global: {
        stubs: {
          Teleport: {
            template: '<div><slot /></div>',
          },
        },
      },
    })
  }

  it('renders when visible', () => {
    const wrapper = mountDialog({ message: 'Удалить?' })
    expect(wrapper.text()).toContain('Удалить?')
  })

  it('does not render when hidden', () => {
    const wrapper = mountDialog({ visible: false })
    expect(wrapper.find('.overlay').exists()).toBe(false)
  })

  it('renders default title and confirm text', () => {
    const wrapper = mountDialog()
    expect(wrapper.text()).toContain('Подтверждение')
    expect(wrapper.text()).toContain('Да')
  })

  it('renders custom title and confirm text', () => {
    const wrapper = mountDialog({ title: 'Выход', confirmText: 'Выйти' })
    expect(wrapper.text()).toContain('Выход')
    expect(wrapper.text()).toContain('Выйти')
  })

  it('applies danger class when danger prop is true', () => {
    const wrapper = mountDialog({ danger: true })
    expect(wrapper.find('.btn-danger').exists()).toBe(true)
  })
})
