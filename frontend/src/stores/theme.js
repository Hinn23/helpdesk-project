import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const saved = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const current = ref(saved || (prefersDark ? 'dark' : 'light'))

  watch(current, (val) => {
    localStorage.setItem('theme', val)
    document.documentElement.setAttribute('data-theme', val)
  }, { immediate: true })

  function toggle() {
    current.value = current.value === 'dark' ? 'light' : 'dark'
  }

  return { current, toggle }
})
