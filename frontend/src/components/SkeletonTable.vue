<template>
  <div class="card" style="padding: 0; overflow: hidden;">
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Статус</th>
            <th>Приоритет</th>
            <th>Категория</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in rows" :key="i">
            <td><div class="skeleton" style="width: 32px; height: 14px;"></div></td>
            <td><div class="skeleton" style="width: 180px; height: 14px;"></div></td>
            <td><div class="skeleton" style="width: 80px; height: 22px; border-radius: 6px;"></div></td>
            <td><div class="skeleton" style="width: 70px; height: 22px; border-radius: 6px;"></div></td>
            <td><div class="skeleton" style="width: 100px; height: 14px;"></div></td>
            <td><div class="skeleton" style="width: 64px; height: 24px; border-radius: 8px;"></div></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({ rows: { type: Number, default: 5 } })
</script>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, var(--border-light) 25%, var(--bg-hover) 50%, var(--border-light) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

[data-theme="dark"] .skeleton {
  background: linear-gradient(90deg, #1e2233 25%, #262a3a 50%, #1e2233 75%);
  background-size: 200% 100%;
}
</style>
