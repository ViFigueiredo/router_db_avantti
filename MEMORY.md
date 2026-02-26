# Memórias e Conhecimento Acumulado do Agente

## Decisões Arquiteturais
- **Multi-tenant**: O sistema utiliza um banco PostgreSQL (Neon) central para armazenar as configurações de cada projeto/tenant, incluindo credenciais de seus respectivos SQL Servers.
- **Conexão Dinâmica**: O router gerencia um pool de conexões dinâmicas para diferentes instâncias de SQL Server usando a biblioteca `mssql`.
- **Segurança**: Cada projeto tem sua própria API Key. O middleware `server/middleware/auth.ts` valida a chave e injeta as configurações do banco no contexto da requisição.
- **Validação**: Todas as entradas (criação de projeto e execução de query) são validadas com Zod.