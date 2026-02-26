<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const { fetchApi } = useApi()
const toast = useToast()

const projects = ref([])
const isLoading = ref(true)
const isModalOpen = ref(false)
const availableDatabases = ref<string[]>([])
const availableTables = ref<string[]>([])
const isLoadingDiscovery = ref(false)

const newProject = ref({
  name: '',
  slug: '',
  sqlServer: {
    database: '',
    allowed_tables: ''
  }
})

const selectedTables = ref<string[]>([])

const fetchProjects = async () => {
  try {
    isLoading.value = true
    const response = await fetchApi('/api/projects/')
    projects.value = Array.isArray(response) ? response : []
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível carregar os projetos', life: 3000 })
  } finally {
    // Delay slightly to prevent flicker on very fast loads
    setTimeout(() => isLoading.value = false, 400)
  }
}

const fetchDatabases = async () => {
  try {
    isLoadingDiscovery.value = true
    const response: any = await fetchApi('/api/projects/discover/databases')
    availableDatabases.value = response.databases
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Erro de Conexão', detail: 'Verifique as credenciais globais no .env', life: 5000 })
  } finally {
    isLoadingDiscovery.value = false
  }
}

const fetchTables = async (dbName: string) => {
  if (!dbName) return
  try {
    isLoadingDiscovery.value = true
    const response: any = await fetchApi(`/api/projects/discover/tables/${dbName}`)
    availableTables.value = response.tables
    selectedTables.value = []
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível listar as tabelas.', life: 3000 })
  } finally {
    isLoadingDiscovery.value = false
  }
}

const slugify = (text: string) => {
  return text
    .toString()
    .normalize('NFD')                   // Normalize special characters
    .replace(/[\u0300-\u036f]/g, '')    // Remove accents
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')               // Replace spaces with -
    .replace(/[^\w-]+/g, '')            // Remove all non-word chars
    .replace(/--+/g, '-')               // Replace multiple - with single -
}

watch(() => newProject.value.name, (newName) => {
  newProject.value.slug = slugify(newName)
})

watch(() => newProject.value.sqlServer.database, (newDb) => {
  if (newDb) fetchTables(newDb)
  else availableTables.value = []
})

const createProject = async () => {
  if (!newProject.value.name || !newProject.value.slug || !newProject.value.sqlServer.database) {
    toast.add({ severity: 'warn', summary: 'Atenção', detail: 'Preencha todos os campos obrigatórios', life: 3000 })
    return
  }

  try {
    const payload = {
      ...newProject.value,
      sqlServer: {
        ...newProject.value.sqlServer,
        allowed_tables: selectedTables.value.join(',')
      }
    }
    
    await fetchApi('/api/projects/', {
      method: 'POST',
      body: payload
    })
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Projeto criado com sucesso!', life: 3000 })
    isModalOpen.value = false
    resetForm()
    fetchProjects()
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Erro', detail: error.data?.detail || 'Erro ao criar projeto', life: 5000 })
  }
}

const resetForm = () => {
  newProject.value = {
    name: '',
    slug: '',
    sqlServer: { database: '', allowed_tables: '' }
  }
  selectedTables.value = []
}

onMounted(() => {
  fetchProjects()
  fetchDatabases()
})
</script>

<template>
  <div class="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-slate-900 rounded-[2.5rem] p-12 text-white shadow-2xl shadow-indigo-500/20">
      <div class="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-indigo-500/20 rounded-full blur-[100px]"></div>
      <div class="absolute bottom-0 left-0 -mb-20 -ml-20 w-72 h-72 bg-purple-500/10 rounded-full blur-[80px]"></div>
      
      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[10px] font-bold uppercase tracking-widest mb-4">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            Painel de Controle
          </div>
          <h2 class="text-4xl md:text-5xl font-black m-0 tracking-tight">Projetos Ativos</h2>
          <p class="text-slate-400 mt-4 text-lg max-w-xl leading-relaxed">Gerencie seus tenants e configure acessos granulares às tabelas do SQL Server global.</p>
        </div>
        
        <Button 
          label="Novo Projeto" 
          icon="pi pi-plus" 
          size="large"
          class="!bg-white !text-slate-900 !border-none !rounded-2xl !px-8 !py-4 !font-bold hover:!bg-indigo-50 transition-colors shadow-xl"
          @click="isModalOpen = true" 
        />
      </div>
    </div>

    <!-- Content Section -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div v-for="i in 3" :key="i" class="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800">
        <Skeleton width="40%" height="1.5rem" class="mb-4" />
        <Skeleton width="80%" height="1rem" class="mb-8" />
        <Skeleton height="100px" class="rounded-2xl" />
      </div>
    </div>

    <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-32 bg-white dark:bg-slate-900 rounded-[3rem] border-2 border-dashed border-slate-200 dark:border-slate-800 transition-all hover:border-indigo-500 group">
      <div class="w-24 h-24 bg-slate-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mb-8 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
        <i class="pi pi-box text-5xl text-slate-300 group-hover:text-indigo-500"></i>
      </div>
      <h3 class="text-2xl font-bold text-slate-900 dark:text-white">Nenhum projeto ainda</h3>
      <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Comece criando seu primeiro tenant agora mesmo.</p>
      <Button label="Criar Primeiro Projeto" variant="text" class="mt-6 !font-bold !text-indigo-600" @click="isModalOpen = true" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div v-for="project in projects" :key="project.id" class="group bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 p-1 hover:border-indigo-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-indigo-500/5">
        <div class="p-7">
          <div class="flex justify-between items-start mb-6">
            <div class="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-500">
              <i class="pi pi-database text-xl"></i>
            </div>
            <Tag :value="project.database_connections[0]?.database" severity="secondary" class="!bg-slate-100 !text-slate-600 !dark:bg-slate-800 !dark:text-slate-400 !font-bold !px-3 !py-1 !rounded-lg" />
          </div>
          
          <h3 class="text-xl font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 transition-colors">{{ project.name }}</h3>
          <p class="text-sm font-mono text-slate-400 mt-1 mb-8">@{{ project.slug }}</p>
          
          <div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800/50 mb-6">
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Chave de Acesso</span>
              <i class="pi pi-copy text-slate-300 hover:text-indigo-500 cursor-pointer transition-colors" v-tooltip="'Copiar API Key'"></i>
            </div>
            <code class="text-xs text-slate-600 dark:text-slate-300 break-all select-all block font-mono">{{ project.api_key }}</code>
          </div>
          
          <div class="flex items-center justify-between text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            <span>Criado em {{ new Date(project.created_at).toLocaleDateString() }}</span>
            <div class="flex gap-1">
              <div v-for="i in 3" :key="i" class="w-1 h-1 rounded-full bg-slate-200 dark:bg-slate-700"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modern Dialog -->
    <Dialog v-model:visible="isModalOpen" modal :draggable="false" :dismissableMask="true" class="w-[90vw] max-w-[550px]">
      <template #header>
        <div class="flex flex-col">
          <span class="text-2xl font-black text-slate-900 dark:text-white tracking-tight">Configurar Novo Tenant</span>
          <span class="text-xs font-bold text-indigo-500 uppercase tracking-widest mt-1">Integração SQL Server</span>
        </div>
      </template>
      
      <div class="space-y-8 py-4">
        <div class="grid grid-cols-1 gap-6">
          <div class="flex flex-col gap-2">
            <label class="text-xs font-black text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">Identificação</label>
            <InputText v-model="newProject.name" placeholder="Nome do Cliente / Projeto" class="!rounded-2xl !p-4 !bg-slate-100/50 !dark:bg-slate-800/50 !border-slate-200 !dark:border-slate-700 focus:!ring-2 focus:!ring-indigo-500 transition-all" />
          </div>
          
          <div class="flex flex-col gap-2">
            <label class="text-xs font-black text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">Slug do Gateway</label>
            <div class="relative">
              <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 font-mono text-sm">/</span>
              <InputText v-model="newProject.slug" placeholder="cliente-alpha" class="w-full !pl-8 !rounded-2xl !p-4 !bg-slate-100/50 !dark:bg-slate-800/50 !border-slate-200 !dark:border-slate-700 focus:!ring-2 focus:!ring-indigo-500 transition-all" />
            </div>
          </div>
        </div>

        <div class="bg-indigo-50/50 dark:bg-indigo-500/5 rounded-[2rem] p-8 border border-indigo-100 dark:border-indigo-500/10">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
              <i class="pi pi-database text-sm"></i>
            </div>
            <span class="font-bold text-slate-800 dark:text-white">Conexão de Dados</span>
          </div>

          <div class="space-y-6">
            <div class="flex flex-col gap-2">
              <label class="text-[10px] font-black text-indigo-700 dark:text-indigo-400 uppercase tracking-widest ml-1">Banco de Dados de Destino</label>
              <Select 
                v-model="newProject.sqlServer.database" 
                :options="availableDatabases" 
                placeholder="Selecione na instância global..."
                :loading="isLoadingDiscovery"
                class="!rounded-xl !border-slate-200 !dark:border-slate-700 !bg-white !dark:bg-slate-900 shadow-sm"
              />
            </div>
            
            <div v-if="newProject.sqlServer.database" class="flex flex-col gap-2 animate-in fade-in slide-in-from-top-2 duration-500">
              <label class="text-[10px] font-black text-indigo-700 dark:text-indigo-400 uppercase tracking-widest ml-1">Tabelas Permitidas (Scope)</label>
              <MultiSelect 
                v-model="selectedTables" 
                :options="availableTables" 
                placeholder="Selecione as tabelas..."
                display="chip"
                :loading="isLoadingDiscovery"
                class="!rounded-xl !border-slate-200 !dark:border-slate-700 !bg-white !dark:bg-slate-900 shadow-sm"
                filter
              />
              <p class="text-[10px] text-slate-500 italic mt-1 ml-1">Vazio = Acesso total ao banco selecionado.</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-4">
          <Button label="Cancelar" variant="text" class="!text-slate-500 !font-bold" @click="isModalOpen = false" />
          <Button label="Finalizar e Gerar Key" icon="pi pi-bolt" @click="createProject" class="!bg-indigo-600 !border-none !rounded-2xl !px-8 !font-bold shadow-xl shadow-indigo-500/20" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
:deep(.p-select-label), :deep(.p-multiselect-label) {
  @apply !p-4 !font-semibold !text-slate-700 dark:!text-slate-200;
}

:deep(.p-skeleton) {
  @apply !bg-slate-100 dark:!bg-slate-800;
}

.animate-in {
  animation-fill-mode: forwards;
}
</style>
