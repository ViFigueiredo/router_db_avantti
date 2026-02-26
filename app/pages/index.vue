<script setup lang="ts">
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
    toast.add({ title: 'Erro', description: 'Não foi possível listar os bancos de dados. Verifique o .env do backend.', color: 'red' })
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
    toast.add({ title: 'Erro', description: 'Não foi possível listar as tabelas.', color: 'red' })
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
    toast.add({ title: 'Sucesso', description: 'Projeto criado com sucesso!', color: 'green' })
    isModalOpen.value = false
    fetchProjects()
  } catch (error: any) {
    toast.add({ 
      title: 'Erro', 
      description: error.data?.detail || 'Erro ao criar projeto', 
      color: 'red' 
    })
  }
}

onMounted(() => {
  fetchProjects()
  fetchDatabases()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold">Projetos</h2>
        <p class="text-gray-500">Gerencie seus tenants e bancos de dados</p>
      </div>
      <UButton icon="i-heroicons-plus" @click="isModalOpen = true">Novo Projeto</UButton>
    </div>

    <UCard v-if="isLoading" class="flex justify-center p-8">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary" />
    </UCard>

    <div v-else-if="projects.length === 0" class="text-center py-20 bg-white dark:bg-gray-800 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-700">
      <UIcon name="i-heroicons-folder-open" class="w-12 h-12 mx-auto text-gray-400 mb-4" />
      <p class="text-gray-500">Nenhum projeto encontrado.</p>
      <UButton variant="link" @click="isModalOpen = true">Criar meu primeiro projeto</UButton>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <UCard v-for="project in projects" :key="project.id" class="hover:shadow-lg transition-shadow">
        <template #header>
          <div class="flex justify-between items-start">
            <div>
              <h3 class="font-bold text-lg">{{ project.name }}</h3>
              <p class="text-sm text-gray-500">{{ project.slug }}</p>
            </div>
            <UBadge color="primary" variant="subtle">SQL Server</UBadge>
          </div>
        </template>
        
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">Banco:</span>
            <span class="font-medium">{{ project.database_connections[0]?.database }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">API Key:</span>
            <span class="font-mono text-xs">{{ project.api_key }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">Criado em:</span>
            <span>{{ new Date(project.created_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Modal Novo Projeto -->
    <UModal v-model="isModalOpen">
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold leading-6">Novo Projeto</h3>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" class="-my-1" @click="isModalOpen = false" />
          </div>
        </template>

        <form @submit.prevent="createProject" class="space-y-4">
          <UFormGroup label="Nome do Projeto" required>
            <UInput v-model="newProject.name" placeholder="Ex: Cliente Alpha" />
          </UFormGroup>
          <UFormGroup label="Slug (Identificador)" required>
            <UInput v-model="newProject.slug" placeholder="ex: cliente-alpha" />
          </UFormGroup>

          <div class="pt-4 border-t dark:border-gray-700">
            <h4 class="font-medium mb-3 text-sm text-gray-700 dark:text-gray-300">Configuração do Banco</h4>
            <div class="space-y-4">
              <UFormGroup label="Selecionar Banco de Dados" required>
                <USelect 
                  v-model="newProject.sqlServer.database" 
                  :options="availableDatabases" 
                  placeholder="Selecione um banco..."
                  :loading="isLoadingDiscovery"
                />
              </UFormGroup>
              
              <UFormGroup v-if="newProject.sqlServer.database" label="Selecionar Tabelas (Opcional)">
                <div class="max-h-40 overflow-y-auto border dark:border-gray-700 rounded p-2 space-y-1">
                  <div v-for="table in availableTables" :key="table" class="flex items-center gap-2">
                    <UCheckbox v-model="selectedTables" :value="table" :label="table" />
                  </div>
                </div>
                <p class="text-xs text-gray-500 mt-1">Se nenhuma for selecionada, todas serão permitidas.</p>
              </UFormGroup>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-4">
            <UButton color="gray" variant="ghost" @click="isModalOpen = false">Cancelar</UButton>
            <UButton type="submit">Criar Projeto</UButton>
          </div>
        </form>
      </UCard>
    </UModal>
  </div>
</template>
