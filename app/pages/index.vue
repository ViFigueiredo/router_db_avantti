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
    console.error('Erro ao buscar projetos:', error)
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível carregar os projetos', life: 3000 })
  } finally {
    isLoading.value = false
  }
}

const fetchDatabases = async () => {
  try {
    isLoadingDiscovery.value = true
    const response: any = await fetchApi('/api/projects/discover/databases')
    availableDatabases.value = response.databases
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível listar os bancos de dados. Verifique o .env do backend.', life: 5000 })
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

watch(() => newProject.value.sqlServer.database, (newDb) => {
  if (newDb) {
    fetchTables(newDb)
  } else {
    availableTables.value = []
  }
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
    toast.add({ 
      severity: 'error', 
      summary: 'Erro', 
      detail: error.data?.detail || 'Erro ao criar projeto', 
      life: 5000 
    })
  }
}

const resetForm = () => {
  newProject.value = {
    name: '',
    slug: '',
    sqlServer: {
      database: '',
      allowed_tables: ''
    }
  }
  selectedTables.value = []
}

onMounted(() => {
  fetchProjects()
  fetchDatabases()
})
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header Section -->
    <div class="flex justify-between items-end bg-surface-0 dark:bg-surface-800 p-8 rounded-2xl border border-surface-200 dark:border-surface-700 shadow-sm">
      <div>
        <h2 class="text-3xl font-black text-surface-900 dark:text-surface-0 m-0 tracking-tight">Projetos</h2>
        <p class="text-surface-500 dark:text-surface-400 mt-2 text-lg font-medium">Gerencie seus tenants e bancos de dados SQL Server</p>
      </div>
      <Button 
        label="Novo Projeto" 
        icon="pi pi-plus" 
        size="large"
        rounded
        class="font-bold px-6 py-3 shadow-lg shadow-primary-500/20"
        @click="isModalOpen = true" 
      />
    </div>

    <!-- Data Section -->
    <div v-if="isLoading">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Skeleton v-for="i in 3" :key="i" height="200px" class="rounded-2xl" />
      </div>
    </div>

    <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-32 bg-surface-0 dark:bg-surface-800 rounded-3xl border-2 border-dashed border-surface-200 dark:border-surface-700 transition-all hover:border-primary-500 group">
      <div class="w-20 h-20 bg-surface-100 dark:bg-surface-700 rounded-full flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
        <i class="pi pi-folder-open text-4xl text-surface-400 group-hover:text-primary-500"></i>
      </div>
      <p class="text-surface-500 dark:text-surface-400 text-xl font-medium">Nenhum projeto encontrado.</p>
      <Button label="Criar meu primeiro projeto" variant="link" class="mt-2 font-bold" @click="isModalOpen = true" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card v-for="project in projects" :key="project.id" class="rounded-2xl border border-surface-200 dark:border-surface-700 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden group">
        <template #header>
          <div class="h-2 bg-primary-500"></div>
        </template>
        <template #title>
          <div class="flex justify-between items-start pt-2">
            <div>
              <span class="text-xl font-bold text-surface-900 dark:text-surface-0 leading-tight block">{{ project.name }}</span>
              <span class="text-sm font-mono text-primary-500 mt-1 block">@{{ project.slug }}</span>
            </div>
            <Tag value="SQL SERVER" severity="info" rounded class="font-bold text-[10px] px-3" />
          </div>
        </template>
        <template #content>
          <div class="space-y-4 mt-2">
            <div class="p-3 bg-surface-50 dark:bg-surface-900 rounded-xl border border-surface-100 dark:border-surface-800">
              <div class="flex items-center gap-3 mb-3">
                <i class="pi pi-database text-primary-500"></i>
                <div class="flex flex-col">
                  <span class="text-[10px] uppercase font-bold text-surface-400 tracking-wider">Database</span>
                  <span class="text-sm font-semibold text-surface-700 dark:text-surface-200">{{ project.database_connections[0]?.database }}</span>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <i class="pi pi-key text-primary-500"></i>
                <div class="flex flex-col flex-1 overflow-hidden">
                  <span class="text-[10px] uppercase font-bold text-surface-400 tracking-wider">API Key</span>
                  <span class="text-xs font-mono text-surface-600 dark:text-surface-400 truncate select-all">{{ project.api_key }}</span>
                </div>
              </div>
            </div>
            
            <div class="flex justify-between items-center px-1 text-[11px] text-surface-400 font-medium">
              <span>Criado em: {{ new Date(project.created_at).toLocaleDateString() }}</span>
              <i class="pi pi-arrow-right group-hover:translate-x-1 transition-transform"></i>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Modal Novo Projeto -->
    <Dialog v-model:visible="isModalOpen" modal header="Novo Projeto" :style="{ width: '500px' }" class="p-fluid rounded-2xl">
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-plus-circle text-primary-500 text-xl"></i>
          <span class="text-xl font-bold">Novo Projeto</span>
        </div>
      </template>
      
      <div class="space-y-6 pt-2">
        <div class="flex flex-col gap-2">
          <label for="name" class="font-bold text-sm text-surface-700 dark:text-surface-200">Nome do Projeto</label>
          <InputText id="name" v-model="newProject.name" placeholder="Ex: Cliente Alpha" />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="slug" class="font-bold text-sm text-surface-700 dark:text-surface-200">Slug (Identificador Único)</label>
          <InputText id="slug" v-model="newProject.slug" placeholder="ex: cliente-alpha" />
        </div>

        <Divider align="left">
          <div class="inline-flex items-center gap-2">
            <i class="pi pi-cog"></i>
            <span class="text-xs font-bold uppercase tracking-widest">Configuração do Banco</span>
          </div>
        </Divider>

        <div class="flex flex-col gap-2">
          <label for="db" class="font-bold text-sm text-surface-700 dark:text-surface-200">Selecionar Banco de Dados</label>
          <Select 
            id="db"
            v-model="newProject.sqlServer.database" 
            :options="availableDatabases" 
            placeholder="Selecione um banco..."
            :loading="isLoadingDiscovery"
            class="w-full"
          />
        </div>
        
        <div v-if="newProject.sqlServer.database" class="flex flex-col gap-2 animate-fade-in">
          <label class="font-bold text-sm text-surface-700 dark:text-surface-200">Selecionar Tabelas (Opcional)</label>
          <MultiSelect 
            v-model="selectedTables" 
            :options="availableTables" 
            placeholder="Escolha as tabelas permitidas"
            display="chip"
            :loading="isLoadingDiscovery"
            class="w-full"
            filter
          />
          <small class="text-surface-500 italic">Se nenhuma for selecionada, todas serão permitidas por padrão.</small>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3 pt-4">
          <Button label="Cancelar" variant="text" severity="secondary" @click="isModalOpen = false" class="font-bold" />
          <Button label="Criar Projeto" icon="pi pi-check" @click="createProject" class="font-bold px-6 shadow-md shadow-primary-500/20" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
