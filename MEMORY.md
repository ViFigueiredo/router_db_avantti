# Memórias e Conhecimento Acumulado do Agente

## Decisões Arquiteturais
- **Backend Python (FastAPI)**: Migração do backend de Nuxt para Python para melhor performance e compatibilidade com drivers de banco de dados específicos.
- **SQLite para Configurações**: Uso de SQLite local para armazenar configurações de projetos e tenants, simplificando o setup e eliminando a dependência de bancos externos (Neon/PostgreSQL) para metadados.
- **Conexão Dinâmica SQL Server**: O backend Python utiliza `pymssql` para gerenciar conexões dinâmicas sob demanda.
- **Segurança**: Autenticação via `x-api-key` no header, validada contra o banco SQLite.
- **Sistema de Logs**: Implementado sistema de logs unificado no diretório `/logs`. O backend Python e o frontend Nuxt (Server e Client) registram eventos detalhados (data/hora, rota, módulo, erro/debug) para facilitar a depuração.