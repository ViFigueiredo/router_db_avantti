<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const { fetchApi } = useApi()
const toast = useToast()

const apiKey = ref('')
const sqlQuery = ref('SELECT TOP 10 * FROM sys.tables')
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
  <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white dark:bg-slate-900 p-10 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-100 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-[10px] font-bold uppercase tracking-widest mb-3">
          Console de Desenvolvedor
        </div>
        <h2 class="text-3xl font-black text-slate-900 dark:text-white m-0 tracking-tight">Query Playground</h2>
        <p class="text-slate-500 dark:text-slate-400 mt-2 font-medium">Valide suas conexões e execute scripts SQL em tempo real.</p>
      </div>
      
      <div class="flex items-center gap-3">
        <div class="p-1 bg-slate-50 dark:bg-slate-800 rounded-2xl flex gap-1">
          <Button icon="pi pi-history" variant="text" class="!text-slate-400" v-tooltip="'Histórico'" />
          <Button icon="pi pi-save" variant="text" class="!text-slate-400" v-tooltip="'Salvar Query'" />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Editor Section -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 overflow-hidden shadow-sm">
          <div class="p-8 space-y-8">
            <div class="flex flex-col gap-3">
              <label class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Autenticação</label>
              <div class="relative">
                <i class="pi pi-key absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
                <InputText v-model="apiKey" placeholder="Cole sua API Key aqui..." class="w-full !pl-11 !rounded-2xl !p-4 !bg-slate-50 !dark:bg-slate-800 !border-none focus:!ring-2 focus:!ring-indigo-500 transition-all font-mono text-xs" />
              </div>
            </div>
            
            <div class="flex flex-col gap-3">
              <label class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] ml-1">Script SQL</label>
              <div class="relative group">
                <div class="absolute -inset-1 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-[1.5rem] opacity-0 group-focus-within:opacity-10 transition-opacity duration-500"></div>
                <Textarea 
                  v-model="sqlQuery" 
                  rows="12" 
                  class="relative w-full !rounded-2xl !p-6 !bg-slate-50 !dark:bg-slate-800 !border-none focus:!ring-0 transition-all font-mono text-sm leading-relaxed resize-none"
                  placeholder="SELECT * FROM ..."
                />
              </div>
            </div>
            
            <Button 
              label="Executar Script"
              icon="pi pi-play-circle" 
              class="w-full !bg-indigo-600 !border-none !rounded-2xl !py-5 !font-bold shadow-xl shadow-indigo-500/20 hover:scale-[1.02] active:scale-95 transition-all"
              :loading="isLoading"
              @click="executeQuery"
            />
          </div>
        </div>
        
        <div class="p-6 bg-amber-50 dark:bg-amber-500/5 rounded-2xl border border-amber-100 dark:border-amber-500/10">
          <div class="flex gap-3">
            <i class="pi pi-info-circle text-amber-500 mt-1"></i>
            <div>
              <span class="block text-xs font-bold text-amber-700 dark:text-amber-400 uppercase tracking-wider mb-1">Dica de Segurança</span>
              <p class="text-[11px] text-amber-600/80 dark:text-amber-500/60 leading-relaxed font-medium">As queries são executadas com as permissões do usuário configurado no .env para o banco do tenant.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Section -->
      <div class="lg:col-span-8">
        <div class="h-full flex flex-col bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden min-h-[600px]">
          <div class="px-8 py-6 border-b border-slate-50 dark:border-slate-800 flex justify-between items-center bg-slate-50/30 dark:bg-slate-800/30">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-500/10 flex items-center justify-center">
                <i class="pi pi-table text-indigo-500 text-sm"></i>
              </div>
              <span class="font-bold text-slate-700 dark:text-slate-200">Dataset de Retorno</span>
            </div>
            <div class="flex items-center gap-2">
              <Tag v-if="results.length" :value="`${results.length} registros`" class="!bg-indigo-500 !text-white !font-bold !px-3 !rounded-full" />
              <Button v-if="results.length" icon="pi pi-download" variant="text" size="small" class="!text-slate-400" />
            </div>
          </div>

          <div class="flex-1 relative">
            <div v-if="!results.length && !isLoading" class="absolute inset-0 flex flex-col items-center justify-center p-12 text-center">
              <div class="w-20 h-20 bg-slate-50 dark:bg-slate-800 rounded-3xl flex items-center justify-center mb-6 border border-slate-100 dark:border-slate-800">
                <i class="pi pi-database text-3xl text-slate-200 dark:text-slate-700"></i>
              </div>
              <h4 class="text-xl font-bold text-slate-400 dark:text-slate-600">Aguardando Execução</h4>
              <p class="text-sm text-slate-400/80 dark:text-slate-600/80 mt-2 max-w-xs font-medium">Insira a chave do projeto e seu script SQL para visualizar os dados.</p>
            </div>

            <div v-else-if="isLoading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm z-10">
              <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="4" />
              <p class="mt-4 text-xs font-bold text-indigo-500 uppercase tracking-[0.2em] animate-pulse">Processando Dataset...</p>
            </div>

            <div v-else class="h-full">
              <DataTable 
                :value="results" 
                stripedRows 
                paginator 
                :rows="12" 
                size="small"
                responsiveLayout="scroll"
                class="modern-table"
                paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                currentPageReportTemplate="{first} a {last} de {totalRecords}"
              >
                <Column v-for="col in columns" :key="col.field" :field="col.field" :header="col.header" sortable class="whitespace-nowrap"></Column>
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
  @apply !bg-transparent !border-t !border-slate-50 dark:!border-slate-800 !p-4;
}

:deep(.p-paginator-current) {
  @apply !text-[10px] !font-bold !text-slate-400 !uppercase !tracking-widest;
}

.animate-in {
  animation-fill-mode: forwards;
}
</style>
