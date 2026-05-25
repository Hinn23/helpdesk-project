<template>
  <div class="form-group">
    <label v-if="label">{{ label }}</label>
    <component
      :is="tag"
      :class="['form-control', inputClass]"
      :value="modelValue"
      @input="onInput"
      v-bind="$attrs"
    >
      <slot />
    </component>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  tag: { type: String, default: 'input' },
  inputClass: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

function onInput(e) {
  emit('update:modelValue', e.target.value)
}
</script>
