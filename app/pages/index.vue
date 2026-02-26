<script setup lang="ts">
const { fetchApi } = useApi()
const toast = useToast()

const projects = ref([])
const isLoading = ref(true)
const isModalOpen = ref(false)

const newProject = ref({
  name: '',
  slug: '',
  sqlServer: {
    host: '',
    port: 1433,
    database: '',
    username: '',
    password: ''
  }
})

const fetchProjects = async () => {
  try {
    isLoading.value = true
    // Note: Since we don't have a GET /api/projects yet, we might need to add it to the backend
    // For now, let's assume it returns an empty list if not implemented
    const response = await fetchApi('/api/projects/')
    projects.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Erro ao buscar projetos:', error)
  } finally {
    isLoading.value = false
  }
}

const createProject = async () => {
  try {
    await fetchApi('/api/projects/', {
      method: 'POST',
      body: newProject.value
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

onMounted(fetchProjects)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold">Projetos</h2>
        <p class="text-gray-500">Gerencie seus tenants e conexões SQL Server</p>
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
            <h4 class="font-medium mb-3">Conexão SQL Server</h4>
            <div class="grid grid-cols-2 gap-4">
              <UFormGroup label="Host" class="col-span-2">
                <UInput v-model="newProject.sqlServer.host" placeholder="ex: 192.168.1.10" />
              </UFormGroup>
              <UFormGroup label="Porta">
                <UInput v-model.number="newProject.sqlServer.port" type="number" />
              </UFormGroup>
              <UFormGroup label="Banco de Dados">
                <UInput v-model="newProject.sqlServer.database" />
              </UFormGroup>
              <UFormGroup label="Usuário">
                <UInput v-model="newProject.sqlServer.username" />
              </UFormGroup>
              <UFormGroup label="Senha">
                <UInput v-model="newProject.sqlServer.password" type="password" />
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
