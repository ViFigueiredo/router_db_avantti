<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 flex font-sans">
    <!-- Sidebar -->
    <aside class="w-72 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-r border-slate-200 dark:border-slate-800 flex flex-col h-screen sticky top-0 z-40 transition-all duration-300">
      <div class="p-8">
        <div class="flex items-center gap-3 group cursor-pointer">
          <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
            <i class="pi pi-database text-white text-xl"/>
          </div>
          <div class="flex flex-col">
            <span class="text-xl font-black text-slate-900 dark:text-white tracking-tight">Router DB</span>
            <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">Gateway Pro</span>
          </div>
        </div>
      </div>
      
      <nav class="flex-1 px-4 space-y-1.5 mt-2">
        <div class="px-4 mb-4 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">Menu Principal</div>
        
        <NuxtLink
          to="/"
          class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 font-semibold no-underline group relative overflow-hidden"
          :class="[
            $route.path === '/' 
              ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-indigo-500'
          ]"
        >
          <div v-if="$route.path === '/'" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-indigo-600 rounded-r-full"/>
          <i class="pi pi-chart-bar text-lg" :class="{ 'scale-110': $route.path === '/' }"/>
          <span>Dashboard</span>
        </NuxtLink>

        <NuxtLink
          to="/projects"
          class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 font-semibold no-underline group relative overflow-hidden"
          :class="[
            $route.path === '/projects' 
              ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-indigo-500'
          ]"
        >
          <div v-if="$route.path === '/projects'" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-indigo-600 rounded-r-full"/>
          <i class="pi pi-box text-lg" :class="{ 'scale-110': $route.path === '/projects' }"/>
          <span>Projetos</span>
        </NuxtLink>
        
        <NuxtLink
          to="/playground"
          class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 font-semibold no-underline group relative overflow-hidden"
          :class="[
            $route.path === '/playground' 
              ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400' 
              : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-indigo-500'
          ]"
        >
          <div v-if="$route.path === '/playground'" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-indigo-600 rounded-r-full"/>
          <i class="pi pi-code text-lg" :class="{ 'scale-110': $route.path === '/playground' }"/>
          <span>Playground</span>
        </NuxtLink>
      </nav>
      
      <div class="p-6 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
        <!-- Appearance toggle removed -->
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
      <!-- Top Header (Breadcrumbs/User) -->
      <header class="h-20 bg-white/50 dark:bg-slate-900/50 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-10 flex items-center justify-between z-30">
        <div class="flex items-center gap-2 text-sm font-medium text-slate-500">
          <span class="hover:text-indigo-500 cursor-pointer transition-colors">Sistema</span>
          <i class="pi pi-chevron-right text-[10px]"/>
          <span class="text-slate-900 dark:text-white capitalize font-bold">{{ $route.path === '/' ? 'Dashboard' : $route.path.replace('/', '') }}</span>
        </div>
        
        <div class="flex items-center gap-4">
          <div class="h-10 w-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold shadow-md border-2 border-white dark:border-slate-800">
            AV
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="flex-1 overflow-y-auto p-10 custom-scrollbar">
        <div class="max-w-6xl mx-auto pb-20">
          <slot />
        </div>
      </div>
    </main>
    
    <Toast position="bottom-right" />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
const isDark = ref(false)

onMounted(() => {
  // Check initial preference
  isDark.value = document.documentElement.classList.contains('dark') || 
                 localStorage.getItem('theme') === 'dark' ||
                 (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
  
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --primary-500: #4f46e5;
  --font-family: 'Plus Jakarta Sans', sans-serif;
}

body {
  margin: 0;
  font-family: 'Plus Jakarta Sans', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.no-underline {
  text-decoration: none !important;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155;
}

/* Fix PrimeVue & Tailwind conflicts */
.p-button {
  @apply transition-all duration-200;
}

.p-dialog-mask {
  backdrop-filter: blur(4px);
  z-index: 1100 !important;
}

.p-dialog {
  @apply rounded-3xl overflow-hidden border-none shadow-2xl shadow-indigo-500/10 bg-white dark:bg-slate-900;
  max-height: 90vh;
}


.p-dialog-header {
  @apply bg-white dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800 p-6;
}

.p-dialog-content {
  @apply p-8 bg-white dark:bg-slate-900;
}

.p-dialog-footer {
  @apply bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 p-6;
}

/* Fix transparency in PrimeVue Select/Dropdown lists */
.p-select-overlay, .p-multiselect-overlay, .p-dropdown-panel {
  @apply bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-xl !important;
  opacity: 1 !important;
  background-color: rgb(255, 255, 255) !important;
  z-index: 2000 !important;
}

.dark .p-select-overlay, .dark .p-multiselect-overlay, .dark .p-dropdown-panel {
  background-color: rgb(15, 23, 42) !important; /* slate-900 */
}

.p-select-list-container, .p-multiselect-list-container, .p-dropdown-items-wrapper {
  @apply bg-white dark:bg-slate-900 !important;
  background-color: rgb(255, 255, 255) !important;
}

.dark .p-select-list-container, .dark .p-multiselect-list-container, .dark .p-dropdown-items-wrapper {
  background-color: rgb(15, 23, 42) !important;
}

.p-select-option, .p-multiselect-option {
  @apply text-slate-700 dark:text-slate-300 !important;
}

/* Custom Toast Styling */
.p-toast {
  @apply !w-96 !max-w-[90vw];
}

.p-toast-message {
  @apply !rounded-2xl !border-none !shadow-2xl !backdrop-blur-xl !my-3;
}

.p-toast-message-content {
  @apply !py-4 !px-5 !gap-4;
}

/* Success Toast */
.p-toast-message-success {
  @apply !bg-emerald-50/90 dark:!bg-emerald-900/20 !text-emerald-900 dark:!text-emerald-100 !border-l-4 !border-emerald-500;
}
.p-toast-message-success .p-toast-message-icon {
  @apply !text-emerald-500;
}

/* Error Toast */
.p-toast-message-error {
  @apply !bg-red-50/90 dark:!bg-red-900/20 !text-red-900 dark:!text-red-100 !border-l-4 !border-red-500;
}
.p-toast-message-error .p-toast-message-icon {
  @apply !text-red-500;
}

/* Warn Toast */
.p-toast-message-warn {
  @apply !bg-amber-50/90 dark:!bg-amber-900/20 !text-amber-900 dark:!text-amber-100 !border-l-4 !border-amber-500;
}
.p-toast-message-warn .p-toast-message-icon {
  @apply !text-amber-500;
}

/* Info Toast */
.p-toast-message-info {
  @apply !bg-blue-50/90 dark:!bg-blue-900/20 !text-blue-900 dark:!text-blue-100 !border-l-4 !border-blue-500;
}
.p-toast-message-info .p-toast-message-icon {
  @apply !text-blue-500;
}

.p-toast-detail {
  @apply !mt-1 !text-sm !opacity-90;
}

.p-toast-summary {
  @apply !font-bold !text-base;
}

.p-toast-icon-close {
  @apply !w-6 !h-6 !rounded-lg hover:!bg-black/5 dark:hover:!bg-white/10 !transition-colors;
}
</style>
