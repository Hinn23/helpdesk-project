import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const messages = ref([])

  function add(text, type = 'success', duration = 3500) {
    const id = Date.now() + Math.random()
    messages.value.push({ id, text, type })
    setTimeout(() => {
      messages.value = messages.value.filter(m => m.id !== id)
    }, duration)
  }

  function success(text) { add(text, 'success') }
  function error(text) { add(text, 'error', 5000) }
  function info(text) { add(text, 'info') }

  return { messages, add, success, error, info }
})
