<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div v-for="msg in toast.messages" :key="msg.id" :class="['toast', `toast-${msg.type}`]">
        <CheckCircle v-if="msg.type === 'success'" :size="16" :strokeWidth="2.5" />
        <XCircle v-else :size="16" :strokeWidth="2.5" />
        <span>{{ msg.text }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { CheckCircle, XCircle } from 'lucide-vue-next'
import { useToastStore } from '../stores/toast'
const toast = useToastStore()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 72px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  pointer-events: auto;
  max-width: 380px;
}

.toast-success {
  background: #065f46;
  color: #d1fae5;
  border: 1px solid #059669;
}

.toast-error {
  background: #7f1d1d;
  color: #fecaca;
  border: 1px solid #dc2626;
}

.toast-info {
  background: #1e3a5f;
  color: #bfdbfe;
  border: 1px solid #3b82f6;
}

[data-theme="dark"] .toast-success {
  background: #064e3b;
  border-color: #10b981;
}

[data-theme="dark"] .toast-error {
  background: #450a0a;
  border-color: #ef4444;
}

[data-theme="dark"] .toast-info {
  background: #172554;
  border-color: #60a5fa;
}

.toast-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-leave-active {
  transition: all 0.25s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px) scale(0.9);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
