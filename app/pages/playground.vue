<!-- eslint-disable @typescript-eslint/no-explicit-any -->
<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const { fetchApi } = useApi()
const toast = useToast()

const apiKey = ref('')
const sqlQuery = ref('SELECT TOP 10 * FROM sys.tables')
const queryLimit = ref(1000)
const results = ref<Record<string, unknown>[]>([])
const isLoading = ref(false)

const executeQuery = async () => {

  try {
    isLoading.value = true
    const response = await fetchApi<{ data: Record<string, unknown>[] }>('/api/query/', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey.value
      },
      body: {
        sql: sqlQuery.value,
        limit: queryLimit.value
      }
    })

    results.value = response.data
    toast.add({ severity: 'success', summary: 'Sucesso', detail: 'Query executada com sucesso!', life: 3000 })
  } catch (error) {
    const err = error as { data?: { detail?: string } };
    toast.add({
      severity: 'error',
      summary: 'Erro na Query',
      detail: err.data?.detail || 'Erro ao executar consulta',
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

const copyCode = () => {
  const code = `curl -X POST "http://localhost:8000/api/query/" \\
  -H "x-api-key: SUA_CHAVE_AQUI" \\
  -H "Content-Type: application/json" \\
  -d '{ "sql": "SELECT * FROM Clientes", "page": 1, "limit": 50 }'`
  navigator.clipboard.writeText(code)
  toast.add({ severity: 'info', summary: 'Copiado', detail: 'Exemplo cURL copiado!', life: 2000 })
}

const mockResponse = JSON.stringify({
  "success": true,
  "data": [
    {
      "id": 1,
      "nome": "Cliente Exemplo",
      "email": "cliente@exemplo.com"
    }
  ],
  "count": 1,
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}, null, 2)

const copyMock = () => {
  navigator.clipboard.writeText(mockResponse)
  toast.add({ severity: 'info', summary: 'Copiado', detail: 'Mock de resposta copiado!', life: 2000 })
}
</script>

<template>
  <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Header Section -->
    <div
      class="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white dark:bg-slate-900 p-10 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm">
      <div>
        <div
          class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-[10px] font-bold uppercase tracking-widest mb-3">
          Console de Desenvolvedor
        </div>
        <h2 class="text-3xl font-black text-slate-900 dark:text-white m-0 tracking-tight">Query Playground</h2>
        <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Valide suas conexões e execute scripts SQL em
          tempo real.</p>
      </div>

      <div class="flex items-center gap-3">
        <div class="p-1 bg-slate-50 dark:bg-slate-800 rounded-2xl flex gap-1">
          <Button v-tooltip="'Histórico'" icon="pi pi-history" variant="text" class="!text-slate-400" />
          <Button v-tooltip="'Salvar Query'" icon="pi pi-save" variant="text" class="!text-slate-400" />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Documentation Section -->
      <div class="lg:col-span-12">
        <div
          class="bg-indigo-600 dark:bg-indigo-900 rounded-[2rem] p-8 text-white relative overflow-hidden shadow-2xl shadow-indigo-500/20">
          <div class="absolute top-0 right-0 -mt-10 -mr-10 w-64 h-64 bg-white/10 rounded-full blur-3xl" />

          <div class="flex flex-col md:flex-row gap-8 relative z-10">
            <div class="flex-1 space-y-4">
              <div
                class="inline-flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider backdrop-blur-sm">
                <i class="pi pi-book" /> Documentação Rápida
              </div>
              <h3 class="text-2xl font-bold">Como integrar com sua aplicação</h3>
              <p class="text-indigo-100 leading-relaxed max-w-2xl">
                Utilize a API REST do Router DB para executar consultas seguras.
                Todas as requisições devem ser autenticadas via header <code
                  class="bg-black/20 px-2 py-0.5 rounded font-mono text-sm">x-api-key</code>.
              </p>
            </div>

            <div
              class="flex-1 bg-black/20 rounded-xl p-6 backdrop-blur-sm border border-white/10 font-mono text-xs overflow-x-auto">
              <div
                class="flex justify-between items-center mb-2 text-indigo-200 uppercase tracking-widest text-[10px] font-bold">
                <span>Exemplo cURL</span>
                <i v-tooltip="'Copiar'" class="pi pi-copy cursor-pointer hover:text-white transition-colors"
                  @click="copyCode" />
              </div>
              <pre class="text-emerald-300">
curl -X POST "http://localhost:8000/api/query/" \
  -H "x-api-key: SUA_CHAVE_AQUI" \
  -H "Content-Type: application/json" \
  -d '{ "sql": "SELECT * FROM Clientes", "page": 1, "limit": 50 }'
</pre>
            </div>

            <div
              class="flex-1 bg-black/20 rounded-xl p-6 backdrop-blur-sm border border-white/10 font-mono text-xs overflow-x-auto">
              <div
                class="flex justify-between items-center mb-2 text-indigo-200 uppercase tracking-widest text-[10px] font-bold">
                <span>Mock de Resposta (JSON)</span>
                <i v-tooltip="'Copiar'" class="pi pi-copy cursor-pointer hover:text-white transition-colors"
                  @click="copyMock" />
              </div>
              <pre class="text-amber-300">{{ mockResponse }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Editor Section -->
      <div class="lg:col-span-4 space-y-6">
        <div
          class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 overflow-hidden shadow-sm">
          <div class="p-8 space-y-8">
            <div class="flex flex-col gap-3">
              <label
                class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Autenticação</label>
              <div class="relative">
                <i class="pi pi-key absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <InputText v-model="apiKey" placeholder="Cole sua API Key aqui..."
                  class="w-full !pl-11 !rounded-2xl !p-4 !bg-slate-50 !dark:bg-slate-800 !border-none focus:!ring-2 focus:!ring-indigo-500 transition-all font-mono text-xs" />
              </div>
            </div>

            <div class="flex flex-col gap-3">
              <label
                class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Script
                SQL</label>
              <div class="relative group">
                <div
                  class="absolute -inset-1 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-[1.5rem] opacity-0 group-focus-within:opacity-10 transition-opacity duration-500" />
                <Textarea v-model="sqlQuery" rows="12"
                  class="relative w-full !rounded-2xl !p-6 !bg-slate-50 !dark:bg-slate-800 !border-none focus:!ring-0 transition-all font-mono text-sm leading-relaxed resize-none"
                  placeholder="SELECT * FROM ..." />
              </div>
            </div>

            <div class="flex flex-col gap-3">
              <label
                class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Limite
                de Linhas</label>
              <div class="relative">
                <i class="pi pi-list absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <InputNumber v-model="queryLimit" :min="1" :max="5000" placeholder="1000"
                  class="w-full !rounded-2xl !bg-slate-50 !dark:bg-slate-800 !border-none focus:!ring-2 focus:!ring-indigo-500 transition-all font-mono text-xs"
                  input-class="!pl-11 !py-4 !w-full !bg-transparent !border-none !text-slate-700 !dark:text-slate-200" />
              </div>
            </div>

            <Button label="Executar Script" icon="pi pi-play-circle"
              class="w-full !bg-indigo-600 !border-none !rounded-2xl !py-5 !font-bold shadow-xl shadow-indigo-500/20 hover:scale-[1.02] active:scale-95 transition-all"
              :loading="isLoading" @click="executeQuery" />
          </div>
        </div>

        <div class="p-6 bg-amber-50 dark:bg-amber-500/5 rounded-2xl border border-amber-100 dark:border-amber-500/10">
          <div class="flex gap-3">
            <i class="pi pi-info-circle text-amber-500 mt-1" />
            <div>
              <span
                class="block text-xs font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider mb-1">Dica de
                Segurança</span>
              <p class="text-[11px] text-amber-600/80 dark:text-amber-500/60 leading-relaxed font-medium">As queries são
                executadas com as permissões do usuário configurado no .env para o banco do tenant.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Section -->
      <div class="lg:col-span-8">
        <div
          class="h-full flex flex-col bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden min-h-[600px]">
          <div
            class="px-8 py-6 border-b border-slate-50 dark:border-slate-800 flex justify-between items-center bg-slate-50/30 dark:bg-slate-800/30">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center">
                <i class="pi pi-table text-indigo-500 text-sm" />
              </div>
              <span class="font-bold text-slate-700 dark:text-slate-200">Dataset de Retorno</span>
            </div>
            <div class="flex items-center gap-2">
              <Tag v-if="results.length" :value="`${results.length} registros`"
                class="!bg-indigo-500 !text-white !font-bold !px-3 !rounded-full" />
              <Button v-if="results.length" icon="pi pi-download" variant="text" size="small" class="!text-slate-400" />
            </div>
          </div>

          <div class="flex-1 relative">
            <div v-if="!results.length && !isLoading"
              class="absolute inset-0 flex flex-col items-center justify-center p-12 text-center">
              <div
                class="w-20 h-20 bg-slate-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mb-6 border border-slate-100 dark:border-slate-800">
                <i class="pi pi-database text-3xl text-slate-200 dark:text-slate-700" />
              </div>
              <h4 class="text-xl font-bold text-slate-400 dark:text-slate-600">Aguardando Execução</h4>
              <p class="text-sm text-slate-400/80 dark:text-slate-600/80 mt-2 max-w-xs font-medium">Insira a chave do
                projeto e seu script SQL para visualizar os dados.</p>
            </div>

            <div v-else-if="isLoading"
              class="absolute inset-0 flex flex-col items-center justify-center bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm z-10">
              <ProgressSpinner style="width: 40px; height: 40px" stroke-width="4" />
              <p class="mt-4 text-xs font-bold text-indigo-500 uppercase tracking-[0.2em] animate-pulse">Processando
                Dataset...</p>
            </div>

            <div v-else class="h-full">
              <DataTable :value="results" striped-rows paginator :rows="12" size="small" responsive-layout="scroll"
                class="modern-table"
                paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                current-page-report-template="{first} a {last} de {totalRecords}">
                <Column v-for="col in columns" :key="col.field" :field="col.field" :header="col.header" sortable
                  class="whitespace-nowrap" />
              </DataTable>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.modern-table) {
  @apply text-sm;
}

:deep(.modern-table .p-datatable-thead > tr > th) {
  @apply bg-slate-50/50 dark:bg-slate-800/50 text-slate-400 dark:text-slate-500 font-black uppercase text-[10px] tracking-widest border-b border-slate-100 dark:border-slate-800 p-4;
}

:deep(.modern-table .p-datatable-tbody > tr > td) {
  @apply p-4 text-slate-600 dark:text-slate-400 border-slate-50 dark:border-slate-800/50 font-medium;
}

:deep(.p-paginator) {
  @apply !bg-transparent !border-t !border-slate-50 !p-4;
}

:deep(.dark .p-paginator) {
  @apply !border-slate-800;
}

:deep(.p-paginator-current) {
  @apply !text-[10px] !font-bold !text-slate-400 !uppercase !tracking-widest;
}

.animate-in {
  animation-fill-mode: forwards;
}
</style>
