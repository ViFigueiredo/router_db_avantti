<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

import { useConfirm } from 'primevue/useconfirm'

const { fetchApi } = useApi()
const toast = useToast()
const confirm = useConfirm()

const projects = ref([])
const isLoading = ref(true)
const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref('')
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
    if (availableDatabases.value.length === 0) {
      toast.add({ severity: 'warn', summary: 'Aviso', detail: 'Nenhum banco de dados encontrado na instância.', life: 5000 })
    }
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Erro de Conexão', detail: 'Não foi possível conectar ao SQL Server. Verifique as credenciais no .env do backend.', life: 10000 })
    console.error('Database Discovery Error:', error)
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
      sql_server: {
        ...newProject.value.sqlServer,
        allowed_tables: selectedTables.value.join(',')
      }
    }

    await fetchApi(isEditing.value ? `/api/projects/${editingId.value}` : '/api/projects/', {
      method: isEditing.value ? 'PUT' : 'POST',
      body: payload
    })
    toast.add({ severity: 'success', summary: 'Sucesso', detail: isEditing.value ? 'Projeto atualizado com sucesso!' : 'Projeto criado com sucesso!', life: 3000 })
    isModalOpen.value = false
    resetForm()
    fetchProjects()
  } catch (error: any) {
    let errorMessage = 'Erro ao criar projeto'
    if (error.data) {
      if (Array.isArray(error.data)) {
        // Handle Pydantic validation errors
        const firstError = error.data[0]
        if (firstError.msg && firstError.loc) {
          errorMessage = `${firstError.msg} (${firstError.loc.join('.')})`
        }
      } else if (error.data.detail) {
        errorMessage = error.data.detail
      }
    }
    toast.add({ severity: 'error', summary: 'Erro', detail: errorMessage, life: 5000 })
  }
}

const resetForm = () => {
  newProject.value = {
    name: '',
    slug: '',
    sqlServer: { database: '', allowed_tables: '' }
  }
  selectedTables.value = []
  isEditing.value = false
  editingId.value = ''
}

const openNewProjectModal = () => {
  resetForm()
  isModalOpen.value = true
}

const editProject = (project: any) => {
  isEditing.value = true
  editingId.value = project.id
  newProject.value = {
    name: project.name,
    slug: project.slug,
    sqlServer: {
      database: project.database_connections[0]?.database || '',
      allowed_tables: ''
    }
  }

  if (project.database_connections[0]?.allowed_tables) {
    selectedTables.value = project.database_connections[0].allowed_tables.split(',').filter((t: string) => t)
  } else {
    selectedTables.value = []
  }

  isModalOpen.value = true
}

const deleteProject = (id: string) => {
  confirm.require({
    message: 'Tem certeza que deseja excluir este projeto?',
    header: 'Confirmação',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Excluir',
    rejectLabel: 'Cancelar',
    acceptClass: '!bg-red-600 !border-red-600 hover:!bg-red-700',
    rejectClass: '!text-slate-500 hover:!bg-slate-100',
    accept: async () => {
      try {
        await fetchApi(`/api/projects/${id}`, { method: 'DELETE' })
        toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Projeto excluído com sucesso!', life: 3000 })
        fetchProjects()
      } catch (error: any) {
        toast.add({ severity: 'error', summary: 'Erro', detail: 'Não foi possível excluir o projeto', life: 3000 })
      }
    }
  })
}

const copyApiKey = (key: string) => {
  navigator.clipboard.writeText(key)
  toast.add({ severity: 'info', summary: 'Copiado!', detail: 'Chave de acesso copiada para a área de transferência.', life: 2000 })
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
      <div class="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-indigo-500/20 rounded-full blur-[100px]"/>
      <div class="absolute bottom-0 left-0 -mb-20 -ml-20 w-72 h-72 bg-purple-500/10 rounded-full blur-[80px]"/>

      <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
        <div>
          <div
            class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[10px] font-bold uppercase tracking-widest mb-4">
            <span class="relative flex h-2 w-2">
              <span
                class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"/>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"/>
            </span>
            Painel de Controle
          </div>
          <h2 class="text-4xl md:text-5xl font-black m-0 tracking-tight">Projetos Ativos</h2>
          <p class="text-slate-400 mt-4 text-lg max-w-xl leading-relaxed">Gerencie seus tenants e configure acessos
            granulares às tabelas do SQL Server global.</p>
        </div>

        <Button
label="Novo Projeto" icon="pi pi-plus" size="large"
          class="!bg-white !text-slate-900 !border-none !rounded-2xl !px-8 !py-4 !font-bold hover:!bg-indigo-50 transition-colors shadow-xl"
          @click="openNewProjectModal" />
      </div>
    </div>

    <!-- Content Section -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div
v-for="i in 3" :key="i"
        class="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800">
        <Skeleton width="40%" height="1.5rem" class="mb-4" />
        <Skeleton width="80%" height="1rem" class="mb-8" />
        <Skeleton height="100px" class="rounded-2xl" />
      </div>
    </div>

    <div
v-else-if="projects.length === 0"
      class="flex flex-col items-center justify-center py-32 bg-white dark:bg-slate-900 rounded-[3rem] border-2 border-dashed border-slate-200 dark:border-slate-800 transition-all hover:border-indigo-500 group">
      <div
        class="w-24 h-24 bg-slate-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mb-8 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
        <i class="pi pi-box text-5xl text-slate-300 group-hover:text-indigo-500"/>
      </div>
      <h3 class="text-2xl font-bold text-slate-900 dark:text-white">Nenhum projeto ainda</h3>
      <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Comece criando seu primeiro tenant agora mesmo.</p>
      <Button
label="Criar Primeiro Projeto" variant="text" class="mt-6 !font-bold !text-indigo-600"
        @click="openNewProjectModal" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div
v-for="project in projects" :key="project.id"
        class="group bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 p-1 hover:border-indigo-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-indigo-500/5">
        <div class="p-7">
          <div class="flex justify-between items-start mb-6">
            <div
              class="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-500">
              <i class="pi pi-database text-xl"/>
            </div>
            <Tag
:value="project.database_connections[0]?.database" severity="secondary"
              class="!bg-slate-100 !text-slate-600 !dark:bg-slate-800 !dark:text-slate-400 !font-bold !px-3 !py-1 !rounded-lg" />
          </div>

          <h3 class="text-xl font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 transition-colors">{{
            project.name }}</h3>
          <p class="text-sm font-mono text-slate-400 mt-1 mb-8">@{{ project.slug }}</p>

          <div
            class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800/50 mb-6">
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Chave de Acesso</span>
              <i
v-tooltip="'Copiar API Key'"
                class="pi pi-copy text-slate-300 hover:text-indigo-500 cursor-pointer transition-colors" @click="copyApiKey(project.api_key)"/>
            </div>
            <code
              class="text-xs text-slate-600 dark:text-slate-300 break-all select-all block font-mono">{{ project.api_key }}</code>
          </div>

          <div class="flex items-center justify-between text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            <span>Criado em {{ new Date(project.created_at).toLocaleDateString() }}</span>
            <div class="flex gap-2">
              <Button
v-tooltip="'Editar'" icon="pi pi-pencil" rounded text
                size="small"
                class="!w-7 !h-7 !text-slate-400 hover:!text-indigo-500 hover:!bg-indigo-50 dark:hover:!bg-indigo-500/10" @click="editProject(project)" />
              <Button
v-tooltip="'Excluir'" icon="pi pi-trash" rounded text
                size="small"
                class="!w-7 !h-7 !text-slate-400 hover:!text-red-500 hover:!bg-red-50 dark:hover:!bg-red-500/10" @click="deleteProject(project.id)" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modern Dialog -->
    <Dialog
v-model:visible="isModalOpen" modal :draggable="false" :dismissable-mask="true"
      class="w-[95vw] max-w-[480px]">
      <template #header>
        <div class="flex flex-col">
          <span class="text-xl font-black text-slate-900 dark:text-white tracking-tight">{{ isEditing ? 'Editar Tenant'
            : 'Configurar Novo Tenant' }}</span>
          <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest mt-0.5">Integração SQL
            Server</span>
        </div>
      </template>

      <div class="space-y-6 py-2">
        <div class="grid grid-cols-1 gap-4">
          <div class="flex flex-col gap-1.5">
            <label
              class="text-[10px] font-black text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">Identificação</label>
            <IconField class="w-full">
              <InputIcon class="pi pi-box" />
              <InputText
v-model="newProject.name" placeholder="Nome do Cliente / Projeto"
                class="w-full !pl-10 !rounded-xl" size="small" />
            </IconField>
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-[10px] font-black text-slate-700 dark:text-slate-300 uppercase tracking-widest ml-1">Slug
              do
              Gateway</label>
            <IconField class="w-full">
              <InputIcon class="pi pi-link" />
              <InputText
v-model="newProject.slug" placeholder="cliente-alpha" class="w-full !pl-10 !rounded-xl"
                size="small" />
            </IconField>
          </div>
        </div>

        <div
          class="bg-indigo-50/50 dark:bg-indigo-500/5 rounded-2xl p-6 border border-indigo-100 dark:border-indigo-500/10">
          <div class="flex items-center gap-2.5 mb-4">
            <div
              class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
              <i class="pi pi-database text-xs"/>
            </div>
            <span class="font-bold text-sm text-slate-800 dark:text-white">Conexão de Dados</span>
          </div>

          <div class="space-y-5">
            <div class="flex flex-col gap-1.5">
              <label
                class="text-[9px] font-black text-indigo-700 dark:text-indigo-400 uppercase tracking-widest ml-1">Banco
                de Dados</label>
              <Select
v-model="newProject.sqlServer.database" :options="availableDatabases" placeholder="Selecione..."
                :loading="isLoadingDiscovery" class="w-full !rounded-xl" size="small" filter show-clear />
            </div>

            <div
v-if="newProject.sqlServer.database"
              class="flex flex-col gap-1.5 animate-in fade-in slide-in-from-top-2 duration-500">
              <label
                class="text-[9px] font-black text-indigo-700 dark:text-indigo-400 uppercase tracking-widest ml-1">Tabelas
                (Scope)</label>
              <MultiSelect
v-model="selectedTables" :options="availableTables" placeholder="Selecione as tabelas..."
                :loading="isLoadingDiscovery" class="w-full !rounded-xl" size="small" filter :max-selected-labels="2"
                selected-items-label="{0} tabelas selecionadas" />
              <p class="text-[9px] text-slate-500 italic mt-0.5 ml-1">Vazio = Acesso total ao banco.</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button
label="Cancelar" variant="text" severity="secondary" size="small" class="!rounded-xl"
            @click="isModalOpen = false" />
          <Button
:label="isEditing ? 'Salvar Alterações' : 'Finalizar e Gerar Key'" icon="pi pi-bolt"
            size="small" class="!bg-indigo-600 !border-indigo-600 !text-white !font-bold !px-4 !rounded-xl"
            @click="createProject" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
:deep(.p-select-label),
:deep(.p-multiselect-label) {
  @apply !p-4 !font-semibold !text-slate-700;
}

:deep(.dark .p-select-label),
:deep(.dark .p-multiselect-label) {
  @apply !text-slate-200;
}

:deep(.p-skeleton) {
  @apply !bg-slate-100;
}

:deep(.dark .p-skeleton) {
  @apply !bg-slate-800;
}

.animate-in {
  animation-fill-mode: forwards;
}
</style>
