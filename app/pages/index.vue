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

const isActivityModalOpen = ref(false)
type ProjectApi = {
  name: string
  sql_server?: {
    allowed_tables?: string[]
  }
}

type ActivityLogApi = {
  id: number
  timestamp: string
  method: string
  path: string
  status_code: number
  duration_ms: number
  project_id?: string | null
  project_name?: string | null
  query_body?: string | null
  tables_involved?: string | null
}

type ActivityRow = {
  id: number
  project: string
  status: 'success' | 'error'
  time: string
  raw_timestamp: number
  method: string
  query: string
  tables: string
  connections: string
  requests: number
  min_lat: string
  avg_lat: string
  max_lat: string
}

type DashboardStats = {
  total_projects: number
  total_requests: number
  active_connections: number
  avg_response_time: string
}

type SystemStatus = {
  api_gateway: string
  sql_server: string
  discovery: string
}

const recentActivity = ref<ActivityRow[]>([])
const projects = ref<ProjectApi[]>([])

// Filter Logic
const filters = ref({
  project: null,
  query: '',
  tables: null,
  dateRange: null as Date[] | null,
  minLatency: null as number | null
})

const resetFilters = () => {
  filters.value = {
    project: null,
    query: '',
    tables: null,
    dateRange: null,
    minLatency: null
  }
}

const projectOptions = computed(() => {
  return projects.value.map(p => p.name).filter(Boolean)
})

const tableOptions = computed(() => {
  const allTables = projects.value.flatMap(p => p.sql_server?.allowed_tables || [])
  return [...new Set(allTables)].sort()
})

const filteredActivity = computed(() => {
  let result = [...recentActivity.value]

  // Apply filters
  if (filters.value.project) {
    result = result.filter(log => log.project === filters.value.project)
  }
  if (filters.value.query) {
    result = result.filter(log => log.query.toLowerCase().includes(filters.value.query.toLowerCase()))
  }
  if (filters.value.tables) {
    // Tables in log are comma separated string "table1, table2"
    // Filter table is single string "table1"
    // We want to see if the log involves the selected table
    result = result.filter(log => log.tables.split(',').map(t => t.trim()).includes(filters.value.tables))
  }
  if (filters.value.minLatency !== null) {
    result = result.filter(log => {
      const lat = parseInt(log.avg_lat.replace('ms', ''))
      return lat >= (filters.value.minLatency || 0)
    })
  }

  if (filters.value.dateRange && filters.value.dateRange.length) {
    const startDate = filters.value.dateRange[0]
    const endDate = filters.value.dateRange[1]

    if (startDate) {
      result = result.filter(log => log.raw_timestamp >= startDate.getTime())
    }
    if (endDate) {
      result = result.filter(log => log.raw_timestamp <= endDate.getTime())
    }
  }

  return result
})

// Summary Cards Logic
const summaryStats = computed(() => {
  const totalQueries = filteredActivity.value.length

  const allTables = filteredActivity.value
    .map(log => log.tables)
    .filter(t => t !== '-')
    .join(',')
    .split(',')
    .map(t => t.trim())
    .filter(t => t)
  const uniqueTables = new Set(allTables).size

  const latencies = filteredActivity.value.map(log => parseInt(log.avg_lat.replace('ms', '')))
  const minLat = latencies.length ? Math.min(...latencies) : 0
  const maxLat = latencies.length ? Math.max(...latencies) : 0
  const avgLat = latencies.length ? Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length) : 0

  return {
    totalQueries,
    uniqueTables,
    minLat,
    avgLat,
    maxLat
  }
})

// Auto-refresh logic
const refreshInterval = ref(10000) // Default 10s
const refreshOptions = [
  { label: '10s', value: 10000 },
  { label: '1min', value: 60000 },
  { label: '5min', value: 300000 },
  { label: '10min', value: 600000 },
  { label: '30min', value: 1800000 },
  { label: '1h', value: 3600000 }
]

let refreshTimer: NodeJS.Timeout | null = null

const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(fetchStats, refreshInterval.value)
}

watch(refreshInterval, () => {
  startAutoRefresh()
})

const fetchProjects = async () => {
  try {
    const data = (await fetchApi('/api/projects')) as ProjectApi[]
    projects.value = data
  } catch (error) {
    console.error('Error fetching projects:', error)
  }
}

const fetchStats = async () => {
  try {
    const [statsData, statusData, activityData] = await Promise.all([
      fetchApi('/api/dashboard/stats'),
      fetchApi('/api/dashboard/status'),
      fetchApi('/api/dashboard/activity' + (isActivityModalOpen.value ? '?limit=1000' : ''))
    ])

    stats.value = statsData as DashboardStats
    systemStatus.value = statusData as SystemStatus

    recentActivity.value = (activityData as ActivityLogApi[]).map(log => ({
      id: log.id,
      project: log.project_name || log.project_id || 'System',
      status: log.status_code >= 400 ? 'error' : 'success',
      time: new Date(log.timestamp).toLocaleTimeString(),
      raw_timestamp: new Date(log.timestamp).getTime(), // Added for filtering
      method: log.method,
      query: log.query_body || log.path,
      tables: log.tables_involved || '-',
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

watch(isActivityModalOpen, (isOpen) => {
  if (isOpen) {
    fetchStats()
  }
})

onMounted(() => {
  fetchStats()
  fetchProjects()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})

const copyToClipboard = (text: string) => {
  if (navigator && navigator.clipboard) {
    navigator.clipboard.writeText(text)
  }
}
</script>

<template>
  <div class="space-y-8">
    <!-- Welcome Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Visão Geral</h2>
        <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Acompanhe o desempenho e uso do seu gateway SQL
          em
          tempo real.</p>
      </div>

      <!-- Auto-refresh Selector -->
      <div
        class="flex items-center gap-1 bg-white dark:bg-slate-900 p-1 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm self-start">
        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider ml-2 mr-1">Atualizar</span>
        <Select
v-model="refreshInterval" :options="refreshOptions" option-label="label" option-value="value"
          class="!border-0 !ring-0 !shadow-none !bg-slate-50 dark:!bg-slate-800 !rounded-lg w-20 !h-8 flex items-center justify-between"
          :pt="{
            root: { class: 'flex items-center' },
            label: { class: '!text-xs !font-bold !text-slate-700 dark:!text-slate-200 !py-0 !px-3' },
            trigger: { class: '!w-6 !text-slate-400' }
          }" />
      </div>
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
              <span
class="flex items-center gap-2 text-xs font-bold"
                :class="getStatusConfig(systemStatus?.api_gateway || 'offline').color">
                <span class="relative flex h-2.5 w-2.5">
                  <span
class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    :class="getStatusConfig(systemStatus?.api_gateway || 'offline').ping" />
                  <span
class="relative inline-flex rounded-full h-2.5 w-2.5"
                    :class="getStatusConfig(systemStatus?.api_gateway || 'offline').dot" />
                </span>
                {{ getStatusConfig(systemStatus?.api_gateway || 'offline').label }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">SQL Server</span>
              <span
class="flex items-center gap-2 text-xs font-bold"
                :class="getStatusConfig(systemStatus?.sql_server || 'offline').color">
                <span class="relative flex h-2.5 w-2.5">
                  <span
class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    :class="getStatusConfig(systemStatus?.sql_server || 'offline').ping" />
                  <span
class="relative inline-flex rounded-full h-2.5 w-2.5"
                    :class="getStatusConfig(systemStatus?.sql_server || 'offline').dot" />
                </span>
                {{ getStatusConfig(systemStatus?.sql_server || 'offline').label }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Discovery Service</span>
              <span
class="flex items-center gap-2 text-xs font-bold"
                :class="getStatusConfig(systemStatus?.discovery || 'offline').color">
                <span class="relative flex h-2.5 w-2.5">
                  <span
class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                    :class="getStatusConfig(systemStatus?.discovery || 'offline').ping" />
                  <span
class="relative inline-flex rounded-full h-2.5 w-2.5"
                    :class="getStatusConfig(systemStatus?.discovery || 'offline').dot" />
                </span>
                {{ getStatusConfig(systemStatus?.discovery || 'offline').label }}
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
          <Button
label="Ver tudo" variant="text" size="small" class="!text-indigo-600 !font-bold"
            @click="isActivityModalOpen = true" />
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
              <tr
v-for="activity in recentActivity" :key="activity.id"
                class="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                <td class="p-4 align-top">
                  <div class="flex flex-col">
                    <span class="font-bold text-sm text-slate-700 dark:text-slate-300">{{ activity.project }}</span>
                    <span
class="text-[10px] font-bold uppercase tracking-wider mt-1"
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

    <!-- Activity Log Modal -->
    <Dialog
v-model:visible="isActivityModalOpen" modal :draggable="false" :dismissable-mask="true"
      class="w-[95vw] h-[90vh]">
      <template #header>
        <div class="flex flex-col">
          <span class="text-xl font-black text-slate-900 dark:text-white tracking-tight">Histórico de Atividades</span>
          <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest mt-0.5">Logs Completos</span>
        </div>
      </template>

      <!-- Filters & Summary Cards -->
      <div class="mb-6 space-y-4">
        <!-- Summary Cards -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div
            class="bg-indigo-50 dark:bg-indigo-500/10 p-4 rounded-xl border border-indigo-100 dark:border-indigo-500/20">
            <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-wider block mb-1">Total Queries</span>
            <span class="text-2xl font-black text-slate-900 dark:text-white">{{ summaryStats.totalQueries }}</span>
          </div>
          <div class="bg-slate-50 dark:bg-slate-800 p-4 rounded-xl border border-slate-100 dark:border-slate-700">
            <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Tabelas Únicas</span>
            <span class="text-2xl font-black text-slate-900 dark:text-white">{{ summaryStats.uniqueTables }}</span>
          </div>
          <div
            class="bg-emerald-50 dark:bg-emerald-500/10 p-4 rounded-xl border border-emerald-100 dark:border-emerald-500/20">
            <span class="text-[10px] font-bold text-emerald-500 uppercase tracking-wider block mb-1">Lat. Mínima</span>
            <span class="text-2xl font-black text-slate-900 dark:text-white">{{ summaryStats.minLat }}ms</span>
          </div>
          <div class="bg-blue-50 dark:bg-blue-500/10 p-4 rounded-xl border border-blue-100 dark:border-blue-500/20">
            <span class="text-[10px] font-bold text-blue-500 uppercase tracking-wider block mb-1">Lat. Média</span>
            <span class="text-2xl font-black text-slate-900 dark:text-white">{{ summaryStats.avgLat }}ms</span>
          </div>
          <div class="bg-amber-50 dark:bg-amber-500/10 p-4 rounded-xl border border-amber-100 dark:border-amber-500/20">
            <span class="text-[10px] font-bold text-amber-500 uppercase tracking-wider block mb-1">Lat. Máxima</span>
            <span class="text-2xl font-black text-slate-900 dark:text-white">{{ summaryStats.maxLat }}ms</span>
          </div>
        </div>

        <!-- Filters Toolbar -->
        <div
          class="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">
          <Toolbar class="!rounded-none !border-0 !border-b !border-slate-100 dark:!border-slate-800 !px-2 !py-1">
            <template #start>
              <div class="flex items-center gap-2">
                <i class="pi pi-filter text-slate-500" />
                <span class="font-semibold text-slate-700 dark:text-slate-200">Filtros</span>
              </div>
            </template>
            <template #end>
              <Button label="Limpar" icon="pi pi-times" text size="small" @click="resetFilters" />
            </template>
          </Toolbar>

          <div class="p-6">
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 items-end">
              <div class="flex flex-col gap-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Projeto</span>
                <Select
v-model="filters.project" :options="projectOptions" placeholder="Todos os Projetos" show-clear
                  filter class="w-full" />
              </div>

              <div class="flex flex-col gap-2 xl:col-span-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Query SQL</span>
                <InputText v-model="filters.query" placeholder="Buscar query..." class="w-full" />
              </div>

              <div class="flex flex-col gap-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Tabela</span>
                <Select
v-model="filters.tables" :options="tableOptions" placeholder="Todas as Tabelas" show-clear
                  filter class="w-full" />
              </div>

              <div class="flex flex-col gap-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Período</span>
                <DatePicker
v-model="filters.dateRange" selection-mode="range" :show-time="true" hour-format="24"
                  placeholder="Selecione o intervalo" show-icon :show-on-focus="false" class="w-full" />
              </div>

              <div class="flex flex-col gap-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Latência (mín)</span>
                <InputNumber
v-model="filters.minLatency" :min="0" placeholder="0" suffix=" ms" :show-buttons="false"
                  class="w-full" />
              </div>
            </div>
          </div>
        </div>

        <div
          class="h-full overflow-hidden flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm">
          <DataTable
:value="filteredActivity" scrollable scroll-height="flex" striped-rows table-class="text-sm"
            :row-hover="true" sort-field="raw_timestamp" :sort-order="-1" :pt="{
              root: { class: 'rounded-xl overflow-hidden' },
              header: { class: 'bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-800' }
            }">
            <template #empty>
              <div class="flex flex-col items-center justify-center py-12 text-slate-400">
                <i class="pi pi-search text-4xl mb-4 opacity-50" />
                <p class="font-medium">Nenhuma atividade encontrada</p>
              </div>
            </template>

            <Column field="project" header="Projeto" sortable class="min-w-[200px]">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <div
                    class="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
                    <i class="pi pi-box text-slate-500" />
                  </div>
                  <div class="flex flex-col">
                    <span class="font-bold text-slate-700 dark:text-slate-200">{{ data.project }}</span>
                    <div class="flex items-center gap-1.5 mt-0.5">
                      <Tag
:value="data.method" severity="info" class="!text-[10px] !px-1.5 !py-0.5" :class="{
                        '!bg-blue-100 !text-blue-700': data.method === 'GET',
                        '!bg-green-100 !text-green-700': data.method === 'POST',
                        '!bg-orange-100 !text-orange-700': data.method === 'PUT',
                        '!bg-red-100 !text-red-700': data.method === 'DELETE'
                      }" />
                      <Tag
:value="data.status === 'success' ? '200' : 'ERR'"
                        :severity="data.status === 'success' ? 'success' : 'danger'"
                        class="!text-[10px] !px-1.5 !py-0.5" />
                    </div>
                  </div>
                </div>
              </template>
            </Column>

            <Column field="query" header="Query SQL" class="min-w-[300px] max-w-[500px]">
              <template #body="{ data }">
                <div
                  class="group relative bg-slate-50 dark:bg-slate-900 rounded-lg p-3 border border-slate-100 dark:border-slate-800 font-mono text-xs text-slate-600 dark:text-slate-400">
                  <div class="line-clamp-2">{{ data.query }}</div>
                  <Button
icon="pi pi-copy" text rounded size="small"
                    class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity !w-6 !h-6"
                    @click="() => copyToClipboard(data.query)" />
                </div>
              </template>
            </Column>

            <Column field="tables" header="Tabelas" class="min-w-[150px]">
              <template #body="{ data }">
                <div v-if="data.tables && data.tables !== '-'" class="flex flex-wrap gap-1">
                  <span
v-for="table in data.tables.split(',')" :key="table"
                    class="inline-flex items-center px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 text-xs font-medium text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                    <i class="pi pi-table text-[10px] mr-1.5 opacity-50" />
                    {{ table.trim() }}
                  </span>
                </div>
                <span v-else class="text-slate-400">-</span>
              </template>
            </Column>

            <Column field="raw_timestamp" header="Data/Hora" sortable class="min-w-[150px]">
              <template #body="{ data }">
                <div class="flex flex-col">
                  <span class="font-medium text-slate-700 dark:text-slate-300">{{ data.time }}</span>
                  <span class="text-[10px] text-slate-400">{{ new Date(data.raw_timestamp).toLocaleDateString()
                  }}</span>
                </div>
              </template>
            </Column>

            <Column field="avg_lat" header="Latência" sortable class="min-w-[120px]">
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <div class="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
class="h-full rounded-full" :class="{
                      'bg-emerald-500': parseInt(data.avg_lat) < 200,
                      'bg-amber-500': parseInt(data.avg_lat) >= 200 && parseInt(data.avg_lat) < 1000,
                      'bg-red-500': parseInt(data.avg_lat) >= 1000
                    }" :style="{ width: Math.min(parseInt(data.avg_lat) / 20, 100) + '%' }" />
                  </div>
                  <span
class="text-xs font-bold font-mono" :class="{
                    'text-emerald-600': parseInt(data.avg_lat) < 200,
                    'text-amber-600': parseInt(data.avg_lat) >= 200 && parseInt(data.avg_lat) < 1000,
                    'text-red-600': parseInt(data.avg_lat) >= 1000
                  }">
                    {{ data.avg_lat }}
                  </span>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
    </Dialog>
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
