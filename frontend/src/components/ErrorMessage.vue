<template>
  <div v-if="message" class="error-box">{{ message }}</div>
</template>

<script setup>
defineProps({ message: { type: String, default: '' } })
</script>
