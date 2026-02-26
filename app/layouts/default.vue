<template>
  <div class="min-h-screen bg-surface-50 dark:bg-surface-900 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-surface-0 dark:bg-surface-800 border-r border-surface-200 dark:border-surface-700 flex flex-col h-screen sticky top-0 shadow-sm">
      <div class="p-6">
        <h1 class="text-2xl font-black text-primary-600 dark:text-primary-400 flex items-center gap-2">
          <i class="pi pi-database text-xl"></i>
          Router DB
        </h1>
      </div>
      
      <nav class="flex-1 px-4 space-y-2">
        <NuxtLink
          to="/"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium no-underline group"
          :class="[
            $route.path === '/' 
              ? 'bg-primary-500 text-white shadow-md shadow-primary-500/20' 
              : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700 hover:text-primary-500'
          ]"
        >
          <i class="pi pi-th-large" :class="{ 'text-white': $route.path === '/' }"></i>
          Projetos
        </NuxtLink>
        
        <NuxtLink
          to="/playground"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium no-underline group"
          :class="[
            $route.path === '/playground' 
              ? 'bg-primary-500 text-white shadow-md shadow-primary-500/20' 
              : 'text-surface-600 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700 hover:text-primary-500'
          ]"
        >
          <i class="pi pi-code" :class="{ 'text-white': $route.path === '/playground' }"></i>
          Playground
        </NuxtLink>
      </nav>
      
      <div class="p-4 border-t border-surface-200 dark:border-surface-700 space-y-2">
        <Button
          :icon="isDark ? 'pi pi-sun' : 'pi pi-moon'"
          :label="isDark ? 'Modo Claro' : 'Modo Escuro'"
          variant="ghost"
          class="w-full justify-start text-surface-600 dark:text-surface-400"
          @click="toggleDarkMode"
        />
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto">
      <div class="p-8 max-w-7xl mx-auto">
        <slot />
      </div>
    </main>
    
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
const isDark = ref(false)

onMounted(() => {
  isDark.value = document.documentElement.classList.contains('dark')
})

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark')
}
</script>

<style>
/* PrimeVue adjustments for Tailwind */
:root {
  --primary-500: #3b82f6;
}

body {
  margin: 0;
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.no-underline {
  text-decoration: none !important;
}
</style>
