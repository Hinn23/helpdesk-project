<template>
  <div class="loader-wrap">
    <div class="spinner"></div>
    <p>{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({ text: { type: String, default: 'Загрузка...' } })
</script>

<style scoped>
.loader-wrap {
  text-align: center;
  padding: 80px 20px;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto 16px;
}

.loader-wrap p {
  color: var(--text-dim);
  font-size: 14px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
