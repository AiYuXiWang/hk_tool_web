import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EnhancedButton from '../EnhancedButton.vue'

describe('EnhancedButton', () => {
  let wrapper

  beforeEach(() => {
    wrapper = null
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('基础渲染', () => {
    it('应该正确渲染默认按钮', () => {
      wrapper = mount(EnhancedButton)

      expect(wrapper.find('.enhanced-button').exists()).toBe(true)
      expect(wrapper.classes()).toContain('enhanced-button--primary')
      expect(wrapper.classes()).toContain('enhanced-button--md')
    })

    it('应该正确设置按钮文本', () => {
      const text = '测试按钮'
      wrapper = mount(EnhancedButton, {
        props: { text }
      })

      expect(wrapper.text()).toContain(text)
    })

    it('应该支持插槽内容', () => {
      const slotContent = '插槽内容'
      wrapper = mount(EnhancedButton, {
        slots: {
          default: slotContent
        }
      })

      expect(wrapper.text()).toContain(slotContent)
    })
  })

  describe('变体样式', () => {
    const variants = ['primary', 'secondary', 'success', 'warning', 'danger', 'info', 'ghost']

    variants.forEach(variant => {
      it(`应该正确应用 ${variant} 变体样式`, () => {
        wrapper = mount(EnhancedButton, {
          props: { variant }
        })

        expect(wrapper.classes()).toContain(`enhanced-button--${variant}`)
      })
    })
  })

  describe('尺寸变体', () => {
    const sizes = ['sm', 'md', 'lg', 'xl']

    sizes.forEach(size => {
      it(`应该正确应用 ${size} 尺寸样式`, () => {
        wrapper = mount(EnhancedButton, {
          props: { size }
        })

        expect(wrapper.classes()).toContain(`enhanced-button--${size}`)
      })
    })
  })

  describe('状态处理', () => {
    it('应该在禁用状态下正确渲染', async () => {
      wrapper = mount(EnhancedButton, {
        props: { disabled: true }
      })

      expect(wrapper.classes()).toContain('enhanced-button--disabled')
      expect(wrapper.attributes('disabled')).toBeDefined()
    })

    it('应该在加载状态下正确渲染', () => {
      wrapper = mount(EnhancedButton, {
        props: { loading: true }
      })

      expect(wrapper.classes()).toContain('enhanced-button--loading')
      expect(wrapper.find('.button-loading').exists()).toBe(true)
      expect(wrapper.find('.icon-loading').exists()).toBe(true)
    })

    it('应该在加载状态下禁用点击', () => {
      wrapper = mount(EnhancedButton, {
        props: { loading: true }
      })

      expect(wrapper.classes()).toContain('enhanced-button--disabled')
    })
  })

  describe('图标处理', () => {
    it('应该正确显示图标', () => {
      const icon = 'icon-dashboard'
      wrapper = mount(EnhancedButton, {
        props: { icon }
      })

      expect(wrapper.find('.button-icon').exists()).toBe(true)
      expect(wrapper.find('.button-icon i').classes()).toContain(icon)
    })

    it('应该在加载状态下隐藏图标', () => {
      const icon = 'icon-dashboard'
      wrapper = mount(EnhancedButton, {
        props: { icon, loading: true }
      })

      expect(wrapper.find('.button-icon').exists()).toBe(false)
    })
  })

  describe('事件处理', () => {
    it('应该正确触发点击事件', async () => {
      wrapper = mount(EnhancedButton)

      await wrapper.trigger('click')

      expect(wrapper.emitted('click')).toBeTruthy()
      expect(wrapper.emitted('click')).toHaveLength(1)
    })

    it('应该在禁用状态下不触发点击事件', async () => {
      wrapper = mount(EnhancedButton, {
        props: { disabled: true }
      })

      await wrapper.trigger('click')

      expect(wrapper.emitted('click')).toBeFalsy()
    })

    it('应该在加载状态下不触发点击事件', async () => {
      wrapper = mount(EnhancedButton, {
        props: { loading: true }
      })

      await wrapper.trigger('click')

      expect(wrapper.emitted('click')).toBeFalsy()
    })

    it('应该正确触发悬停事件', async () => {
      wrapper = mount(EnhancedButton)

      await wrapper.trigger('mouseenter')
      expect(wrapper.emitted('hover')).toBeTruthy()

      await wrapper.trigger('mouseleave')
      expect(wrapper.emitted('leave')).toBeTruthy()
    })
  })

  describe('交互状态', () => {
    it('应该在悬停时添加hover类', async () => {
      wrapper = mount(EnhancedButton)

      await wrapper.trigger('mouseenter')
      expect(wrapper.classes()).toContain('enhanced-button--hovered')

      await wrapper.trigger('mouseleave')
      expect(wrapper.classes()).not.toContain('enhanced-button--hovered')
    })
  })

  describe('无障碍支持', () => {
    it('应该支持键盘导航', async () => {
      wrapper = mount(EnhancedButton)

      // 模拟键盘Enter键
      await wrapper.trigger('keydown.enter')
      expect(wrapper.emitted('click')).toBeTruthy()

      // 清除之前的事件
      wrapper.emitted().click = []

      // 模拟键盘空格键
      await wrapper.trigger('keydown.space')
      expect(wrapper.emitted('click')).toBeTruthy()
    })

    it('应该在禁用状态下不支持键盘操作', async () => {
      wrapper = mount(EnhancedButton, {
        props: { disabled: true }
      })

      await wrapper.trigger('keydown.enter')
      expect(wrapper.emitted('click')).toBeFalsy()
    })
  })

  describe('波纹效果', () => {
    it('应该在点击时创建波纹效果', async () => {
      wrapper = mount(EnhancedButton, {
        props: { rippleEnabled: true }
      })

      // 模拟点击事件
      await wrapper.trigger('click', {
        clientX: 100,
        clientY: 100
      })

      // 检查波纹元素是否存在
      const rippleElement = wrapper.find('.button-ripple')
      expect(rippleElement.exists()).toBe(true)
    })

    it('应该能够禁用波纹效果', () => {
      wrapper = mount(EnhancedButton, {
        props: { rippleEnabled: false }
      })

      expect(wrapper.find('.button-ripple').exists()).toBe(false)
    })
  })

  describe('动画支持', () => {
    it('应该能够禁用动画', () => {
      wrapper = mount(EnhancedButton, {
        props: { animated: false }
      })

      expect(wrapper.classes()).not.toContain('enhanced-button--animated')
    })
  })

  describe('响应式支持', () => {
    it('应该在移动端保持最小点击区域', () => {
      wrapper = mount(EnhancedButton)

      const button = wrapper.find('.enhanced-button')
      const computedStyle = getComputedStyle(button.element)

      // 检查最小高度
      expect(parseInt(computedStyle.minHeight)).toBeGreaterThanOrEqual(40)
    })
  })

  describe('边界情况', () => {
    it('应该处理空的文本内容', () => {
      wrapper = mount(EnhancedButton, {
        props: { text: '' }
      })

      expect(wrapper.text()).toBe('')
    })

    it('应该处理未知的变体', () => {
      // Vue的props验证会处理这个情况，但我们确保组件不会崩溃
      expect(() => {
        wrapper = mount(EnhancedButton, {
          props: { variant: 'unknown' }
        })
      }).toThrow()
    })

    it('应该处理未知的尺寸', () => {
      expect(() => {
        wrapper = mount(EnhancedButton, {
          props: { size: 'unknown' }
        })
      }).toThrow()
    })
  })
})