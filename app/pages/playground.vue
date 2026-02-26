<script setup lang="ts">
const { fetchApi } = useApi()
const toast = useToast()

const apiKey = ref('')
const sqlQuery = ref('SELECT TOP 10 * FROM TabelaExemplo')
const results = ref<any[]>([])
const isLoading = ref(false)

const executeQuery = async () => {
  if (!apiKey.value) {
    toast.add({ title: 'Aviso', description: 'Por favor, insira uma API Key', color: 'orange' })
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
    toast.add({ title: 'Sucesso', description: 'Query executada com sucesso!', color: 'green' })
  } catch (error: any) {
    toast.add({ 
      title: 'Erro na Query', 
      description: error.data?.detail || 'Erro ao executar consulta', 
      color: 'red' 
    })
  } finally {
    isLoading.value = false
  }
}

const columns = computed(() => {
  if (!results.value.length) return []
  return Object.keys(results.value[0]).map(key => ({
    key,
    label: key.charAt(0).toUpperCase() + key.slice(1)
  }))
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold">Query Playground</h2>
      <p class="text-gray-500">Teste suas consultas SQL Server em tempo real</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-1 space-y-4">
        <UCard>
          <template #header>
            <h3 class="font-semibold">Configuração</h3>
          </template>
          
          <div class="space-y-4">
            <UFormGroup label="API Key do Projeto">
              <UInput v-model="apiKey" icon="i-heroicons-key" placeholder="Insira a chave do projeto" />
            </UFormGroup>
            
            <UFormGroup label="SQL Query">
              <UTextarea 
                v-model="sqlQuery" 
                rows="8" 
                class="font-mono text-sm"
                placeholder="SELECT * FROM ..."
              />
            </UFormGroup>
            
            <UButton 
              block 
              icon="i-heroicons-play" 
              :loading="isLoading"
              @click="executeQuery"
            >
              Executar Query
            </UButton>
          </div>
        </UCard>
      </div>

      <div class="lg:col-span-2">
        <UCard class="h-full flex flex-col">
          <template #header>
            <div class="flex justify-between items-center">
              <h3 class="font-semibold">Resultados</h3>
              <UBadge v-if="results.length" color="gray">{{ results.length }} linhas</UBadge>
            </div>
          </template>

          <div v-if="!results.length && !isLoading" class="flex-1 flex flex-col items-center justify-center py-20 text-gray-400">
            <UIcon name="i-heroicons-table-cells" class="w-12 h-12 mb-2" />
            <p>Os resultados da sua query aparecerão aqui</p>
          </div>

          <div v-else-if="isLoading" class="flex-1 flex items-center justify-center py-20">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary" />
          </div>

          <div v-else class="overflow-x-auto">
            <UTable :rows="results" :columns="columns" />
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>
