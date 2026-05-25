import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNotifyStore = defineStore('notify', () => {
  const count = ref(0)
  const items = ref([])
  const soundEnabled = ref(false)

  const hasUnread = computed(() => count.value > 0)

  function add(notification) {
    items.value.unshift({ id: Date.now(), ...notification, read: false })
    count.value++
    if (items.value.length > 50) items.value.pop()
  }

  function markRead() {
    count.value = 0
    items.value.forEach(i => i.read = true)
  }

  return { count, items, hasUnread, add, markRead, soundEnabled }
})
