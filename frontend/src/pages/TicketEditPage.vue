<template>
  <Loader v-if="loading" />
  <TicketForm v-else-if="ticket" :ticket="ticket" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ticketsApi } from '../api/ticketsApi'
import TicketForm from '../components/TicketForm.vue'
import Loader from '../components/Loader.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ticket = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    ticket.value = await ticketsApi.getById(route.params.id)
    if (!auth.isAdmin && Number(auth.userId) !== ticket.value.author_id) {
      router.push('/tasks')
      return
    }
  } catch { router.push('/tasks') }
  finally { loading.value = false }
})
</script>
