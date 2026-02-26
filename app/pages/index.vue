<script setup lang="ts">
const { fetchApi } = useApi()

const stats = ref({
  total_projects: 0,
  total_requests: 15430, // Mocked for now
  active_connections: 0,
  avg_response_time: '45ms'
})

const recentActivity = ref([
  { id: 1, type: 'query', project: 'CookPit', status: 'success', time: '2 min atrás', method: 'SELECT' },
  { id: 2, type: 'query', project: 'CookPit', status: 'error', time: '15 min atrás', method: 'UPDATE' },
  { id: 3, type: 'connection', project: 'Novo Tenant', status: 'success', time: '1 hora atrás', method: 'CONNECT' },
  { id: 4, type: 'query', project: 'CookPit', status: 'success', time: '2 horas atrás', method: 'SELECT' },
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
  <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Welcome Header -->
    <div>
      <h2 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Visão Geral</h2>
      <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Acompanhe o desempenho e uso do seu gateway SQL em tempo real.</p>
    </div>

    <!-- KPI Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
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

      <div class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <i class="pi pi-bolt text-6xl text-amber-500"></i>
        </div>
        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Requisições (24h)</span>
          <span class="text-4xl font-black text-slate-900 dark:text-white">{{ (stats.total_requests / 1000).toFixed(1) }}k</span>
          <span class="text-xs font-medium text-emerald-500 mt-2 flex items-center gap-1">
            <i class="pi pi-arrow-up text-[10px]"></i> +12% vs ontem
          </span>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
          <i class="pi pi-server text-6xl text-blue-500"></i>
        </div>
        <div class="flex flex-col gap-1 relative z-10">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Conexões Ativas</span>
          <span class="text-4xl font-black text-slate-900 dark:text-white">{{ stats.active_connections }}</span>
          <span class="text-xs font-medium text-slate-400 mt-2">Estável</span>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
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

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Activity Feed -->
      <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm">
        <div class="flex items-center justify-between mb-8">
          <h3 class="text-xl font-bold text-slate-900 dark:text-white">Atividade Recente</h3>
          <Button label="Ver tudo" variant="text" size="small" class="!text-indigo-600 !font-bold" />
        </div>
        
        <div class="space-y-6">
          <div v-for="activity in recentActivity" :key="activity.id" class="flex items-center gap-4 group">
            <div 
              class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors"
              :class="activity.status === 'success' ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600' : 'bg-red-50 dark:bg-red-500/10 text-red-600'"
            >
              <i :class="activity.type === 'query' ? 'pi pi-database' : 'pi pi-wifi'" class="text-sm"></i>
            </div>
            
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-0.5">
                <span class="text-sm font-bold text-slate-900 dark:text-white">{{ activity.project }}</span>
                <span 
                  class="text-[10px] px-1.5 py-0.5 rounded font-mono font-bold"
                  :class="activity.status === 'success' ? 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400' : 'bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400'"
                >
                  {{ activity.method }}
                </span>
              </div>
              <p class="text-xs text-slate-500 truncate">Execução de query via API Gateway</p>
            </div>
            
            <span class="text-xs font-medium text-slate-400 shrink-0">{{ activity.time }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Actions / Status -->
      <div class="space-y-6">
        <div class="bg-indigo-600 dark:bg-indigo-900 rounded-[2.5rem] p-8 text-white relative overflow-hidden shadow-2xl shadow-indigo-500/20">
          <div class="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
          
          <h3 class="text-xl font-bold mb-2 relative z-10">Novo Projeto</h3>
          <p class="text-indigo-100 text-sm mb-6 relative z-10">Configure um novo tenant e comece a integrar em segundos.</p>
          
          <NuxtLink to="/projects">
            <Button label="Criar Projeto" class="w-full !bg-white !text-indigo-600 !border-none !font-bold !rounded-xl shadow-lg relative z-10" />
          </NuxtLink>
        </div>

        <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-sm">
            <h3 class="text-sm font-bold text-slate-900 dark:text-white mb-4 uppercase tracking-wider">Status do Sistema</h3>
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
</style>
