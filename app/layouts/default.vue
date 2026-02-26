<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Sidebar -->
    <aside class="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-50">
      <div class="flex flex-col h-full">
        <div class="p-6">
          <h1 class="text-xl font-bold text-primary-600 dark:text-primary-400">Router DB</h1>
        </div>
        
        <nav class="flex-1 px-4 space-y-2">
          <ULink
            to="/"
            class="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors"
            active-class="bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300"
            inactive-class="text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            <UIcon name="i-heroicons-squares-2x2" class="w-5 h-5" />
            Projetos
          </ULink>
          
          <ULink
            to="/playground"
            class="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors"
            active-class="bg-primary-50 text-primary-700 dark:bg-primary-900/50 dark:text-primary-300"
            inactive-class="text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700"
          >
            <UIcon name="i-heroicons-code-bracket" class="w-5 h-5" />
            Playground
          </ULink>
        </nav>
        
        <div class="p-4 border-t border-gray-200 dark:border-gray-700">
          <UButton
            icon="i-heroicons-moon"
            color="gray"
            variant="ghost"
            block
            @click="$colorMode.preference = $colorMode.value === 'dark' ? 'light' : 'dark'"
          >
            Alternar Tema
          </UButton>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="pl-64">
      <div class="p-8">
        <slot />
      </div>
    </main>
    
    <UNotifications />
  </div>
</template>
