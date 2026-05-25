<template>
  <Teleport to="body">
    <div v-if="visible" class="msg-overlay" @click.self="close">
      <div class="msg-modal">
        <div class="msg-sidebar">
          <div class="msg-sidebar-header">
            <h3>Сообщения</h3>
            <button class="msg-close" @click="close">✕</button>
          </div>
          <div v-if="convsLoading" style="padding: 20px; text-align: center; color: var(--text-dim); font-size: 13px;">Загрузка...</div>
          <div v-else-if="!conversations.length" style="padding: 20px; text-align: center; color: var(--text-dim); font-size: 13px;">Нет диалогов</div>
          <div v-else class="conv-list">
            <div v-for="c in conversations" :key="c.user_id" class="conv-item" :class="{ active: activeConv === c.user_id }" @click="openConv(c.user_id)">
              <img v-if="c.avatar" :src="`/api/auth/${c.user_id}/avatar`" class="conv-avatar" />
              <div v-else class="conv-avatar-placeholder">{{ c.name.slice(0, 2).toUpperCase() }}</div>
              <div class="conv-info">
                <span class="conv-name">{{ c.name }}</span>
                <span class="conv-preview">{{ c.last_message }}</span>
              </div>
              <span v-if="c.unread" class="conv-badge">{{ c.unread }}</span>
            </div>
          </div>
        </div>
        <div class="msg-chat">
          <template v-if="activeConv">
            <div class="chat-header">
              <router-link :to="`/users/${activeConv}`" class="chat-user" @click="visible = false">{{ convName }}</router-link>
              <button class="btn btn-secondary btn-xs" @click="closeConv">✕</button>
            </div>
            <div class="chat-messages" ref="chatRef">
              <div v-if="chatLoading" style="text-align: center; color: var(--text-dim); font-size: 13px; padding: 40px;">Загрузка...</div>
              <div v-for="m in messages" :key="m.id" class="msg-bubble" :class="{ mine: m.sender_id === auth.userIdAsNumber }">
                <div class="msg-text">{{ m.text }}</div>
                <div class="msg-time">{{ formatTime(m.created_at) }}</div>
              </div>
            </div>
            <div class="chat-input">
              <input v-model="newMsg" class="form-control" placeholder="Написать сообщение..." @keydown.enter="send" />
              <button class="btn btn-primary btn-sm" :disabled="!newMsg.trim()" @click="send">Отправить</button>
            </div>
          </template>
          <template v-else>
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-dim); font-size: 14px;">Выберите диалог</div>
          </template>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import api from '../api/axios'

defineProps({ visible: Boolean })
const emit = defineEmits(['update:visible'])

const auth = useAuthStore()
const toast = useToastStore()

const conversations = ref([])
const convsLoading = ref(true)
const activeConv = ref(null)
const convName = ref('')
const messages = ref([])
const chatLoading = ref(false)
const newMsg = ref('')
const chatRef = ref(null)
let pollTimer = null

function startPoll() {
  stopPoll()
  pollTimer = setInterval(async () => {
    await loadConvs()
    if (activeConv.value) {
      try {
        const r = await api.get(`/messages/${activeConv.value}`)
        messages.value = r.data
      } catch {}
    }
  }, 3000)
}

function stopPoll() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

async function loadConvs() {
  if (!auth.isAuthenticated) return
  convsLoading.value = true
  try {
    const r = await api.get('/messages/conversations')
    conversations.value = r.data
  } catch {}
  finally { convsLoading.value = false }
}

async function openConv(userId) {
  activeConv.value = userId
  const u = conversations.value.find(c => c.user_id === userId)
  convName.value = u?.name || ''
  chatLoading.value = true
  try {
    const r = await api.get(`/messages/${userId}`)
    messages.value = r.data
    await api.post(`/messages/read/${userId}`)
    if (u) u.unread = 0
    await nextTick()
    if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
  } catch {}
  finally { chatLoading.value = false }
}

function closeConv() { activeConv.value = null }

async function send() {
  if (!newMsg.value.trim() || !activeConv.value) return
  const text = newMsg.value
  newMsg.value = ''
  try {
    await api.post(`/messages/${activeConv.value}`, { text })
    await openConv(activeConv.value)
  } catch { toast.error('Ошибка') }
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function close() { emit('update:visible', false) }

function startConversation(userId, userName) {
  activeConv.value = userId
  convName.value = userName
  openConv(userId)
}

watch(() => auth.isAuthenticated, () => { if (auth.isAuthenticated) loadConvs() })

watch(() => auth.isAuthenticated, (v) => { if (v) startPoll(); else stopPoll() })

onMounted(() => { if (auth.isAuthenticated) { loadConvs(); startPoll() } })
onUnmounted(() => stopPoll())

defineExpose({ startConversation })

window.__reloadMessages = () => { if (auth.isAuthenticated) loadConvs() }
</script>

<style scoped>
.msg-overlay {
  position: fixed; inset: 0; z-index: 900;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
}
.msg-modal {
  width: 720px; height: 520px; display: flex;
  background: var(--bg-card); border-radius: 14px;
  overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.msg-sidebar { width: 260px; border-right: 1px solid var(--border); display: flex; flex-direction: column; }
.msg-sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid var(--border-light); }
.msg-sidebar-header h3 { font-size: 15px; font-weight: 700; }
.msg-close { background: none; border: none; font-size: 18px; cursor: pointer; color: var(--text-muted); }
.conv-list { flex: 1; overflow-y: auto; }
.conv-item { display: flex; align-items: center; gap: 10px; padding: 10px 16px; cursor: pointer; transition: background 0.1s; position: relative; }
.conv-item:hover { background: var(--bg-hover); }
.conv-item.active { background: var(--bg-hover); }
.conv-avatar, .conv-avatar-placeholder { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.conv-avatar-placeholder { background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; }
.conv-info { flex: 1; min-width: 0; }
.conv-name { display: block; font-size: 13px; font-weight: 600; color: var(--text); }
.conv-preview { display: block; font-size: 11px; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conv-badge { background: var(--danger); color: #fff; font-size: 10px; font-weight: 800; min-width: 18px; height: 18px; border-radius: 9px; display: flex; align-items: center; justify-content: center; padding: 0 4px; }
.msg-chat { flex: 1; display: flex; flex-direction: column; }
.chat-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border-light); }
.chat-user { font-weight: 700; font-size: 15px; color: var(--text); text-decoration: none; }
.chat-user:hover { color: var(--primary); }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 8px; }
.msg-bubble { max-width: 70%; padding: 8px 14px; border-radius: 12px; font-size: 14px; line-height: 1.4; }
.msg-bubble.mine { align-self: flex-end; background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
.msg-bubble:not(.mine) { align-self: flex-start; background: var(--bg-input); border: 1px solid var(--border-light); border-bottom-left-radius: 4px; }
.msg-text { word-break: break-word; }
.msg-time { font-size: 10px; opacity: 0.6; margin-top: 4px; text-align: right; }
.chat-input { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid var(--border-light); }
.chat-input .form-control { flex: 1; }
</style>
