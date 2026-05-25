<template>
  <Teleport to="body">
    <div v-if="visible" class="lightbox-overlay" @click.self="close">
      <button class="lightbox-close" @click="close">✕</button>
      <img :src="src" class="lightbox-img" :alt="alt" @click="close" />
    </div>
  </Teleport>
</template>

<script setup>
defineProps({ visible: Boolean, src: String, alt: String })
const emit = defineEmits(['update:visible'])
function close() { emit('update:visible', false) }
</script>

<style scoped>
.lightbox-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.85);
  display: flex; align-items: center; justify-content: center;
  cursor: zoom-out; animation: fadeIn 0.2s ease-out;
}
.lightbox-close {
  position: absolute; top: 16px; right: 20px;
  background: none; border: none; color: #fff;
  font-size: 28px; cursor: pointer; opacity: 0.7;
  transition: opacity 0.2s;
}
.lightbox-close:hover { opacity: 1; }
.lightbox-img {
  max-width: 90vw; max-height: 90vh;
  border-radius: 8px; object-fit: contain;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
