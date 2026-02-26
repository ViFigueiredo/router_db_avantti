<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const { fetchApi } = useApi()
const toast = useToast()

const apiKey = ref('')
const sqlQuery = ref('SELECT TOP 10 * FROM INFORMATION_SCHEMA.TABLES')
const results = ref<any[]>([])
const isLoading = ref(false)

const executeQuery = async () => {
  if (!apiKey.value) {
    toast.add({ severity: 'warn', summary: 'Atenção', detail: 'Por favor, insira uma API Key', life: 3000 })
    return
  }

  try {
    isLoading.value = true
    const response: any = await fetchApi('/api/query/', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey.value
      },
      body: {
        sql: sqlQuery.value
      }
    })
    
    results.value = response.data
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Query executada com sucesso!', life: 3000 })
  } catch (error: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Erro na Query', 
      detail: error.data?.detail || 'Erro ao executar consulta', 
      life: 5000 
    })
  } finally {
    isLoading.value = false
  }
}

const columns = computed(() => {
  if (!results.value.length) return []
  return Object.keys(results.value[0]).map(key => ({
    field: key,
    header: key.charAt(0).toUpperCase() + key.slice(1)
  }))
})
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header Section -->
    <div class="bg-surface-0 dark:bg-surface-800 p-8 rounded-2xl border border-surface-200 dark:border-surface-700 shadow-sm">
      <h2 class="text-3xl font-black text-surface-900 dark:text-surface-0 m-0 tracking-tight">Query Playground</h2>
      <p class="text-surface-500 dark:text-surface-400 mt-2 text-lg font-medium">Teste suas consultas SQL Server em tempo real</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Editor Section -->
      <div class="lg:col-span-4 space-y-6">
        <Card class="rounded-2xl border border-surface-200 dark:border-surface-700 shadow-sm overflow-hidden">
          <template #title>
            <div class="flex items-center gap-2 mb-2">
              <i class="pi pi-sliders-h text-primary-500"></i>
              <span class="text-lg font-bold">Configuração</span>
            </div>
          </template>
          <template #content>
            <div class="space-y-6">
              <div class="flex flex-col gap-2">
                <label for="api-key" class="font-bold text-sm text-surface-700 dark:text-surface-200 uppercase tracking-wider">API Key do Projeto</label>
                <div class="p-input-icon-left w-full">
                  <i class="pi pi-key ml-3" />
                  <InputText id="api-key" v-model="apiKey" placeholder="Insira a chave do projeto" class="w-full pl-10" />
                </div>
              </div>
              
              <div class="flex flex-col gap-2">
                <label for="sql" class="font-bold text-sm text-surface-700 dark:text-surface-200 uppercase tracking-wider">SQL Query</label>
                <Textarea 
                  id="sql"
                  v-model="sqlQuery" 
                  rows="10" 
                  class="font-mono text-sm leading-relaxed"
                  placeholder="SELECT * FROM ..."
                />
              </div>
              
              <Button 
                label="Executar Query"
                icon="pi pi-play" 
                class="w-full font-bold py-4 shadow-lg shadow-primary-500/20"
                :loading="isLoading"
                @click="executeQuery"
              />
            </div>
          </template>
        </Card>
      </div>

      <!-- Results Section -->
      <div class="lg:col-span-8">
        <Card class="h-full flex flex-col rounded-2xl border border-surface-200 dark:border-surface-700 shadow-sm overflow-hidden">
          <template #title>
            <div class="flex justify-between items-center mb-2">
              <div class="flex items-center gap-2">
                <i class="pi pi-table text-primary-500"></i>
                <span class="text-lg font-bold">Resultados</span>
              </div>
              <Tag v-if="results.length" :value="`${results.length} linhas`" severity="secondary" class="font-bold" />
            </div>
          </template>

          <template #content>
            <div v-if="!results.length && !isLoading" class="flex-1 flex flex-col items-center justify-center py-32 text-surface-400">
              <div class="w-16 h-16 bg-surface-50 dark:bg-surface-900 rounded-full flex items-center justify-center mb-4 border border-surface-100 dark:border-surface-800">
                <i class="pi pi-database text-3xl"></i>
              </div>
              <p class="text-lg font-medium">Os resultados aparecerão aqui</p>
              <span class="text-sm mt-1 italic">Configure a API Key e execute sua query</span>
            </div>

            <div v-else-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-32">
              <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
              <p class="mt-4 text-surface-500 font-medium animate-pulse">Processando consulta...</p>
            </div>

            <div v-else class="overflow-x-auto rounded-xl border border-surface-100 dark:border-surface-800">
              <DataTable 
                :value="results" 
                stripedRows 
                paginator 
                :rows="10" 
                size="small"
                responsiveLayout="scroll"
                class="text-sm"
              >
                <Column v-for="col in columns" :key="col.field" :field="col.field" :header="col.header" sortable></Column>
              </DataTable>
            </div>
          </template>
        </Card>
      </div>
    </div>
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

:deep(.p-datatable-thead > tr > th) {
  background: var(--p-surface-50);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.05em;
}

:deep(.p-card-body) {
  padding: 0;
}

:deep(.p-card-content) {
  padding: 1.5rem;
}
</style>
