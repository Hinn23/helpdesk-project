<template>
  <button
    :class="['btn', `btn-${variant}`, sizeClass]"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  disabled: { type: Boolean, default: false },
})

const sizeClass = computed(() => {
  return props.size === 'sm' ? 'btn-sm' : props.size === 'xs' ? 'btn-xs' : ''
})
</script>

<style scoped>
.btn {
  padding: 10px 22px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  line-height: 1;
}

.btn:hover { transform: translateY(-1px); }
.btn:active { transform: scale(0.96); }
.btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none !important; }

.btn-primary { background: var(--primary); color: #fff; box-shadow: 0 2px 8px var(--primary-shadow); }
.btn-primary:hover { background: var(--primary-hover); box-shadow: 0 4px 16px var(--primary-shadow); }

.btn-danger { background: var(--danger); color: #fff; box-shadow: 0 2px 8px var(--danger-shadow); }
.btn-danger:hover { background: var(--danger-hover); box-shadow: 0 4px 16px var(--danger-shadow); }

.btn-secondary { background: var(--bg-hover); color: var(--text-secondary); border: 1px solid var(--border); }
.btn-secondary:hover { background: var(--bg-input); }

.btn-sm { padding: 6px 14px; font-size: 13px; }
.btn-xs { padding: 4px 10px; font-size: 12px; }
</style>
