# Entrega Aula 05 - Documentos e Metadados (LangChain & RAG)

## Exercício 1 - Questões Teóricas

### Pergunta A: Que tipos de dado são aceitos dentro de metadata?
*Resposta:* O LangChain aceita listas e dicionários aninhados nativamente em memória no objeto Document. Porém, algumas Vector Stores (como ChromaDB ou Pinecone) podem emitir erros ou falhar na hora de salvar metadados muito complexos (listas/dicionários), exigindo apenas tipos primitivos (string, integer, boolean, float).

### Pergunta B: O que acontece se você criar um Document sem passar metadata?
*Resposta:* O objeto é criado normalmente e o campo metadata é preenchido com um dicionário vazio {} por padrão.

---

## Exercício 2 - Schema de Metadados

### 1. Tabela do Schema

| Campo | Descrição |
| :--- | :--- |
| fonte | Nome do arquivo .md de origem |
| documento_id | Identificador único do documento |
| chunk_index | Posição sequencial do chunk no documento |
| estrategia | Estratégia de chunking utilizada |
| chunk_size | Configuração de tamanho do chunk |
| chunk_overlap | Configuração de sobreposição de caracteres |
| n_caracteres | Tamanho real do chunk |
| secao_titulo | Título do capítulo ou seção do documento |
| pagina | Número da página no arquivo original |
| data_processamento | Data de indexação do chunk no sistema |

### 2. Justificativa dos Campos Próprios
* *secao_titulo*: Permite responder em qual capítulo/seção o conteúdo está localizado.
* *pagina*: Permite indicar exatamente em qual página do documento original a resposta foi encontrada.
* *data_processamento*: Permite verificar a atualização do dado e evitar informações antigas ou defasadas.

### 3. Exemplo de Chunk Preenchido (JSON)
```json
{
  "fonte": "manual_ia.md",
  "documento_id": "doc_rag_2026_01",
  "chunk_index": 4,
  "estrategia": "RecursiveCharacterTextSplitter",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "n_caracteres": 482,
  "secao_titulo": "Arquitetura RAG",
  "pagina": 12,
  "data_processamento": "2026-08-12"
}