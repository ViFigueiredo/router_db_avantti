<script setup lang="ts">
const { fetchApi } = useApi()

const stats = ref({
  total_projects: 0,
  total_requests: 0,
  active_connections: 0,
  avg_response_time: '0ms'
})

const systemStatus = ref({
  api_gateway: 'online',
  sql_server: 'offline',
  discovery: 'active'
})

const getStatusConfig = (status: string) => {
  const configs: Record<string, { color: string; dot: string; ping: string; label: string }> = {
    online: { color: 'text-emerald-500', dot: 'bg-emerald-500', ping: 'bg-emerald-400', label: 'Online' },
    connected: { color: 'text-emerald-500', dot: 'bg-emerald-500', ping: 'bg-emerald-400', label: 'Conectado' },
    active: { color: 'text-emerald-500', dot: 'bg-emerald-500', ping: 'bg-emerald-400', label: 'Ativo' },
    unstable: { color: 'text-amber-500', dot: 'bg-amber-500', ping: 'bg-amber-400', label: 'Instável' },
    offline: { color: 'text-red-500', dot: 'bg-red-500', ping: 'bg-red-400', label: 'Offline' },
    error: { color: 'text-red-500', dot: 'bg-red-500', ping: 'bg-red-400', label: 'Erro' }
  }
  return configs[status] || configs.offline
}

const recentActivity = ref<any[]>([])

const fetchStats = async () => {
  try {
    const [statsData, statusData, activityData] = await Promise.all([
      fetchApi('/api/dashboard/stats'),
      fetchApi('/api/dashboard/status'),
      fetchApi('/api/dashboard/activity')
    ])

    stats.value = statsData as any
    systemStatus.value = statusData as any

    recentActivity.value = (activityData as any[]).map(log => ({
      id: log.id,
      project: log.project_id || 'System',
      status: log.status_code >= 400 ? 'error' : 'success',
      time: new Date(log.timestamp).toLocaleTimeString(),
      method: log.method,
      query: log.path,
      tables: '-',
      connections: '-',
      requests: 1,
      min_lat: '-',
      avg_lat: `${log.duration_ms}ms`,
      max_lat: '-'
    }))

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

    <!-- KPI Grid Moved to Sidebar -->

    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Quick Actions / Status -->
      <div class="w-full lg:w-80 shrink-0 space-y-6 min-w-0">
        <div
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm">
          <div class="flex items-center justify-between mb-8">
            <h3 class="text-xl font-bold text-slate-900 dark:text-white">Status do Sistema</h3>
          </div>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">API Gateway</span>
              <span class="flex items-center gap-2 text-xs font-bold"
                :class="getStatusConfig(systemStatus.api_gateway).color">
                <span class="relative flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    :class="getStatusConfig(systemStatus.api_gateway).ping" />
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5"
                    :class="getStatusConfig(systemStatus.api_gateway).dot" />
                </span>
                {{ getStatusConfig(systemStatus.api_gateway).label }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">SQL Server</span>
              <span class="flex items-center gap-2 text-xs font-bold"
                :class="getStatusConfig(systemStatus.sql_server).color">
                <span class="relative flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    :class="getStatusConfig(systemStatus.sql_server).ping" />
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5"
                    :class="getStatusConfig(systemStatus.sql_server).dot" />
                </span>
                {{ getStatusConfig(systemStatus.sql_server).label }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Discovery Service</span>
              <span class="flex items-center gap-2 text-xs font-bold"
                :class="getStatusConfig(systemStatus.discovery).color">
                <span class="relative flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    :class="getStatusConfig(systemStatus.discovery).ping" />
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5"
                    :class="getStatusConfig(systemStatus.discovery).dot" />
                </span>
                {{ getStatusConfig(systemStatus.discovery).label }}
              </span>
            </div>
          </div>
        </div>

        <!-- KPI Cards -->
        <div
          class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <i class="pi pi-box text-6xl text-indigo-600" />
          </div>
          <div class="flex flex-col gap-1 relative z-10">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Projetos Ativos</span>
            <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.total_projects }}</span>
          </div>
        </div>

        <div
          class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <i class="pi pi-bolt text-6xl text-amber-500" />
          </div>
          <div class="flex flex-col gap-1 relative z-10">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Requisições</span>
            <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.total_requests }}</span>
          </div>
        </div>

        <div
          class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <i class="pi pi-server text-6xl text-blue-500" />
          </div>
          <div class="flex flex-col gap-1 relative z-10">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Conexões Ativas</span>
            <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.active_connections }}</span>
          </div>
        </div>

        <div
          class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <i class="pi pi-clock text-6xl text-purple-500" />
          </div>
          <div class="flex flex-col gap-1 relative z-10">
            <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Latência Média</span>
            <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.avg_response_time }}</span>
          </div>
        </div>
      </div>

      <!-- Activity Feed -->
      <div
        class="flex-1 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm min-w-0 overflow-hidden">
        <div class="flex items-center justify-between mb-8">
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Atividade Recente</h3>
          <Button label="Ver tudo" variant="text" size="small" class="!text-indigo-600 !font-bold" />
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-100 dark:border-slate-800">
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[150px]">
                  Nome</th>
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[150px]">
                  Query</th>
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[100px]">
                  Tabelas</th>
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 min-w-[140px]">
                  Data/Hora</th>
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 text-center">
                  Conn</th>
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 text-center">
                  Reqs</th>
                <th
                  class="p-4 text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 bg-slate-50/50 dark:bg-slate-800/50 text-center min-w-[140px]">
                  Latência</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50">
              <tr v-for="activity in recentActivity" :key="activity.id"
                class="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
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
                    <span class="text-xs font-mono text-slate-500 cursor-help" :title="activity.query">{{ activity.query
                      }}</span>
                  </div>
                </td>
                <td class="p-4 align-top">
                  <span
                    class="inline-flex text-xs font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded whitespace-nowrap">
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
                    <span class="text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 px-1.5 py-0.5 rounded">{{
                      activity.min_lat }}</span>
                    <span class="text-slate-400">/</span>
                    <span class="text-blue-600 bg-blue-50 dark:bg-blue-500/10 px-1.5 py-0.5 rounded font-bold">{{
                      activity.avg_lat }}</span>
                    <span class="text-slate-400">/</span>
                    <span class="text-amber-600 bg-amber-50 dark:bg-amber-500/10 px-1.5 py-0.5 rounded">{{
                      activity.max_lat }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
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
