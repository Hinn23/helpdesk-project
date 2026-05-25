<template>
  <Teleport to="body">
    <div v-if="visible" class="overlay" @click.self="onCancel">
      <Transition name="modal">
        <div v-if="visible" class="dialog">
          <div class="dialog-title">{{ title }}</div>
          <div class="dialog-text">{{ message }}</div>
          <div class="dialog-actions">
            <button class="btn btn-secondary" @click="onCancel">Отмена</button>
            <button class="btn" :class="confirmClass" @click="onConfirm">{{ confirmText }}</button>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  title: { type: String, default: 'Подтверждение' },
  message: { type: String, default: 'Вы уверены?' },
  confirmText: { type: String, default: 'Да' },
  danger: Boolean,
})

const emit = defineEmits(['confirm', 'cancel'])
const confirmClass = ref('btn-primary')

watch(() => props.danger, (v) => { confirmClass.value = v ? 'btn-danger' : 'btn-primary' }, { immediate: true })

function onConfirm() { emit('confirm') }
function onCancel() { emit('cancel') }
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn 0.2s ease-out;
}

.dialog {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px;
  min-width: 320px;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.dialog-title {
  font-size: 17px; font-weight: 700; margin-bottom: 10px; color: var(--text);
}

.dialog-text {
  font-size: 14px; color: var(--text-secondary); margin-bottom: 24px; line-height: 1.5;
}

.dialog-actions {
  display: flex; gap: 10px; justify-content: flex-end;
}

.modal-enter-active, .modal-leave-active {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-enter-from, .modal-leave-to {
  opacity: 0; transform: scale(0.92);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
