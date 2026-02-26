<script setup lang="ts">
const { fetchApi } = useApi()

const stats = ref({
  total_projects: 0,
  total_requests: 15430, // Mocked for now
  active_connections: 0,
  avg_response_time: '45ms'
})

const recentActivity = ref([
  { id: 1, type: 'query', project: 'CookPit', status: 'success', time: '2025-02-26 14:30:00', method: 'SELECT', query: 'SELECT * FROM Clientes', tables: 'Clientes', connections: 5, requests: 120, min_lat: '20ms', avg_lat: '45ms', max_lat: '150ms' },
  { id: 2, type: 'query', project: 'CookPit', status: 'error', time: '2025-02-26 14:15:00', method: 'UPDATE', query: 'UPDATE Pedidos SET status = 1', tables: 'Pedidos', connections: 5, requests: 15, min_lat: '30ms', avg_lat: '60ms', max_lat: '200ms' },
  { id: 3, type: 'connection', project: 'Novo Tenant', status: 'success', time: '2025-02-26 13:00:00', method: 'CONNECT', query: '-', tables: '-', connections: 1, requests: 5, min_lat: '10ms', avg_lat: '15ms', max_lat: '25ms' },
  { id: 4, type: 'query', project: 'CookPit', status: 'success', time: '2025-02-26 12:30:00', method: 'SELECT', query: 'SELECT count(*) FROM Logs', tables: 'Logs', connections: 4, requests: 300, min_lat: '15ms', avg_lat: '35ms', max_lat: '100ms' },
])

const fetchStats = async () => {
  try {
    const projects = await fetchApi('/api/projects/')
    stats.value.total_projects = Array.isArray(projects) ? projects.length : 0
    stats.value.active_connections = stats.value.total_projects // Assuming 1 conn per project for now
  } catch (error) {
    console.error('Error fetching dashboard stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome Header -->
    <div>
      <h2 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Visão Geral</h2>
      <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Acompanhe o desempenho e uso do seu gateway SQL em
        tempo real.</p>
    </div>

    <!-- KPI Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <i class="pi pi-box text-6xl text-indigo-600"></i>
        </div>
        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Projetos Ativos</span>
          <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.total_projects }}</span>
          <span class="text-xs font-medium text-emerald-500 mt-2 flex items-center gap-1">
            <i class="pi pi-arrow-up text-[10px]"></i> +2 essa semana
          </span>
        </div>
      </div>

      <div
        class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <i class="pi pi-bolt text-6xl text-amber-500"></i>
        </div>
        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Requisições (24h)</span>
          <span class="text-4xl font-black text-slate-900 dark:text-white">{{ (stats.total_requests / 1000).toFixed(1)
            }}k</span>
          <span class="text-xs font-medium text-emerald-500 mt-2 flex items-center gap-1">
            <i class="pi pi-arrow-up text-[10px]"></i> +12% vs ontem
          </span>
        </div>
      </div>

      <div
        class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <i class="pi pi-server text-6xl text-blue-500"></i>
        </div>
        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Conexões Ativas</span>
          <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.active_connections }}</span>
          <span class="text-xs font-medium text-slate-400 mt-2">Estável</span>
        </div>
      </div>

      <div
        class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <i class="pi pi-clock text-6xl text-purple-500"></i>
        </div>
        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Latência Média</span>
          <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.avg_response_time }}</span>
          <span class="text-xs font-medium text-emerald-500 mt-2 flex items-center gap-1">
            <i class="pi pi-check-circle text-[10px]"></i> Performance Ótima
          </span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Activity Feed -->
      <div
        class="lg:col-span-9 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm min-w-0 overflow-hidden">
        <div class="flex items-center justify-between mb-8">
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Atividade Recente</h3>
          <Button label="Ver tudo" variant="text" size="small" class="!text-indigo-600 !font-bold" />
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-100 dark:border-slate-800">
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[150px]">Nome</th>
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[150px]">Query</th>
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[100px]">Tabelas</th>
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[140px]">Data/Hora</th>
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 text-center">Conn</th>
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 text-center">Reqs</th>
                <th class="p-4 text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 text-center min-w-[140px]">Latência</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50">
              <tr v-for="activity in recentActivity" :key="activity.id" class="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                <td class="p-4 align-top">
                  <div class="flex flex-col">
                    <span class="font-bold text-sm text-slate-700 dark:text-slate-300">{{ activity.project }}</span>
                    <span class="text-[10px] font-bold uppercase tracking-wider mt-1" 
                      :class="activity.status === 'success' ? 'text-emerald-500' : 'text-red-500'">
                      {{ activity.method }}
                    </span>
                  </div>
                </td>
                <td class="p-4 align-top">
                  <div class="max-w-[200px] truncate">
                    <span class="text-xs font-mono text-slate-500 cursor-help" :title="activity.query">{{ activity.query }}</span>
                  </div>
                </td>
                <td class="p-4 align-top">
                  <span class="inline-flex text-xs font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded whitespace-nowrap">
                    {{ activity.tables }}
                  </span>
                </td>
                <td class="p-4 align-top">
                  <span class="text-xs text-slate-500 font-mono">{{ activity.time }}</span>
                </td>
                <td class="p-4 align-top text-center">
                  <span class="text-xs font-bold text-indigo-600 dark:text-indigo-400">{{ activity.connections }}</span>
                </td>
                <td class="p-4 align-top text-center">
                  <span class="text-xs font-bold text-slate-600 dark:text-slate-400">{{ activity.requests }}</span>
                </td>
                <td class="p-4 align-top">
                  <div class="flex items-center justify-center gap-1 text-[10px] font-mono">
                    <span class="text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 px-1.5 py-0.5 rounded">{{ activity.min_lat }}</span>
                    <span class="text-slate-400">/</span>
                    <span class="text-blue-600 bg-blue-50 dark:bg-blue-500/10 px-1.5 py-0.5 rounded font-bold">{{ activity.avg_lat }}</span>
                    <span class="text-slate-400">/</span>
                    <span class="text-amber-600 bg-amber-50 dark:bg-amber-500/10 px-1.5 py-0.5 rounded">{{ activity.max_lat }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Quick Actions / Status -->
      <div class="lg:col-span-3 space-y-6 min-w-0">
        <!-- New Project Card Removed -->

        <div
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm">
          <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-4 uppercase tracking-wider">Status do Sistema
          </h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">API Gateway</span>
              <span class="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Online
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">SQL Server</span>
              <span class="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Conectado
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-500">Discovery Service</span>
              <span class="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Ativo
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation-fill-mode: forwards;
}

:deep(.modern-table) {
  @apply text-sm;
}

:deep(.modern-table .p-datatable-thead > tr > th) {
  @apply bg-slate-50/50 dark:bg-slate-800/50 text-slate-400 dark:text-slate-500 font-black uppercase text-[10px] tracking-widest border-b border-slate-100 dark:border-slate-800 p-4 whitespace-nowrap;
}

:deep(.modern-table .p-datatable-tbody > tr > td) {
  @apply p-4 text-slate-600 dark:text-slate-400 border-slate-50 dark:border-slate-800/50 font-medium;
}
</style>
