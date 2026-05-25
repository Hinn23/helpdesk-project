<template>
  <div class="not-found">
    <div class="card" style="text-align: center; padding: 60px 40px; max-width: 480px; margin: 60px auto;">
      <div style="font-size: 64px; font-weight: 800; color: var(--text-dim); line-height: 1; margin-bottom: 16px;">404</div>
      <h2 style="margin-bottom: 8px; color: var(--text);">Страница не найдена</h2>
      <p style="color: var(--text-muted); margin-bottom: 28px; font-size: 15px;">
        Кажется, вы забрели не туда. Такой страницы не существует.
      </p>
      <router-link to="/" class="btn btn-primary">На главную</router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
