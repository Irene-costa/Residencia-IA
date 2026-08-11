# Relatório de Experimentos: Estratégias de Chunking (AULA_04)

---

## 1. Testes 1 a 6 — Chunking por Tamanho e Overlap

Nesta etapa, avaliamos o impacto direto do tamanho do chunk (chunk_size) e do nível de sobreposição (chunk_overlap).

### Tabela Comparativa de Métricas

| Teste | Configuração (chunk_size / chunk_overlap) | Total Chunks | Tam. Médio | Tam. Mínimo | Tam. Máximo | Chunks Sobrepostos | % Overlap |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| *Teste 1* | chunk_size = 200, overlap = 0 | 467 | 200.0 | 18 | 200 | 0 | 0% |
| *Teste 2* | chunk_size = 500, overlap = 0 | 187 | 498.9 | 45 | 500 | 0 | 0% |
| *Teste 3* | chunk_size = 1000, overlap = 0 | 94 | 992.5 | 90 | 1000 | 0 | 0% |
| *Teste 4* | chunk_size = 2000, overlap = 0 | 47 | 1985.0 | 120 | 2000 | 0 | 0% |
| *Teste 5* | chunk_size = 500, overlap = 50 | 208 | 499.1 | 50 | 500 | 207 | 10% |
| *Teste 6* | chunk_size = 500, overlap = 200 | 311 | 499.5 | 200 | 500 | 310 | 40% |

### Análise dos Resultados (Testes 1 a 6)
* *Tamanhos pequenos (200 caracteres):* Geram uma quantidade excessiva de trechos (467 chunks) e cortam palavras/frases no meio, perdendo a coesão.
* *Tamanhos grandes (2000 caracteres):* Reduzem vertiginosamente o volume de chunks (47), mas correm o risco de misturar assuntos distintos dentro da mesma unidade.
* *Efeito do Overlap (50 e 200):* Aumenta o número total de chunks (de 187 para 208 e 311), garantindo continuidade de contexto entre blocos adjacentes.

---

## 2. Teste 7 — Por Parágrafo

Estratégia focada em preservar parágrafos inteiros como unidade natural de contexto.

* *Quantidade de Chunks:* 224
* *Tamanho Médio:* 416.5 caracteres
* *Tamanho Mínimo / Máximo:* 28 / 1.450 caracteres
* *Metadados Associados:* {"tipo": "parágrafo", "fonte": "bioetica_e_ia.md"}
* *Exemplo de Chunk:*
  > "A bioética na inteligência artificial é um campo interdisciplinar que busca analisar os impactos morais e sociais do uso de algoritmos em tomada de decisão."

---

## 3. Teste 8 — Sentenças Agrupadas

Divisão do texto em sentenças individuais com agrupamento fixo de *3 sentenças por chunk*.

* *Quantidade de Chunks:* 191
* *Tamanho Médio:* 488.2 caracteres
* *Tamanho Mínimo / Máximo:* 65 / 890 caracteres
* *Lógica de Agrupamento:* Sentença 1 + Sentença 2 + Sentença 3 -> Chunk 1
* *Análise:* Oferece excelente granulação para busca semântica (RAG), pois evita cortes no meio de ideias semânticas completas.

---

## 4. Teste 9 — Recursive Chunking

Utilização do RecursiveCharacterTextSplitter explorando a hierarquia natural de separadores do Python/LangChain.

* *Separadores Hierárquicos Utilizados:* ["\n\n", "\n", " ", ""] (Parágrafos $\rightarrow$ Linhas $\rightarrow$ Espaços $\rightarrow$ Caracteres).
* *Parâmetros Configurados:* chunk_size = 500, chunk_overlap = 50.
* *Quantidade de Chunks:* 271
* *Tamanho Médio:* 478.0 caracteres
* *Justificativa da Escolha:* É o divisor mais recomendado para documentos de texto geral. Ele tenta primeiro manter parágrafos inteiros; se o parágrafo for maior que 500 caracteres, ele divide em linhas; se ainda for maior, divide em palavras.

---

## 5. Teste 10 — Markdown / Estrutura Semântica

Utilização do MarkdownHeaderTextSplitter para fatiar o documento com base nas seções e títulos (#, ##, ###).

* *Headers Utilizados:* [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
* *Quantidade de Chunks:* 33
* *Tamanho Médio:* 2.827 caracteres
* *Análise:* Preserva 100% o significado semântico e a estrutura do documento. É a melhor estratégia para documentações estruturadas e artigos acadêmicos.
---

## 2. Análise Obrigatória (Respostas às 15 Questões do Roteiro)

### 1. Qual estratégia gerou mais chunks?
O *Teste 1 (Fixo - 200 caracteres, sem overlap)* gerou o maior volume de trechos devido ao tamanho extremamente reduzido da janela de corte.

### 2. Qual gerou menos chunks?
O *Teste 10 (Markdown Headings)* gerou o menor volume, pois preserva seções inteiras delimitadas pelos cabeçalhos do documento.

### 3. Como o tamanho dos chunks variou?
Variou de *18 caracteres* (menor trecho no Teste 1) a *6.400 caracteres* (maior seção semântica no Teste 10). Nos testes de caractere fixo o tamanho é rígido e limitado pelo teto configurado, enquanto nos testes semânticos/estruturais a variação é orgânica.

### 4. Qual estratégia preservou melhor a estrutura dos documentos?
O *Teste 10 (Markdown Splitter)* foi o melhor, pois manteve os títulos (#, ##, ###) vinculados ao conteúdo de suas respectivas seções e guardou essas referências nos metadados.

### 5. Como tabelas foram tratadas?
Como o arquivo de entrada foi convertido para Markdown, as tabelas foram preservadas em sintaxe de barras (|). No entanto, em splitters por caractere (Testes 1 a 6) ou sentença (Teste 8), as linhas das tabelas foram frequentemente cortadas ao meio. Apenas o *Markdown Splitter (Teste 10)* e o *Parágrafo (Teste 7)* mantiveram a tabela inteira em um mesmo bloco.

### 6. Como imagens foram tratadas?
As imagens foram mantidas na marcação padrão do Markdown (![descrição](caminho.png)). O texto das descrições alternativas (alt text) e os caminhos foram preservados dentro dos chunks, sem perda de código de referência.

### 7. Quais informações foram perdidas durante a conversão PDF -> Markdown?
Foram perdidos elementos visuais e de diagramação original, como cabeçalhos e rodapés das páginas do PDF, numeração de páginas, colunas de layout dinâmico e formatação gráfica de fontes e cores.

### 8. O chunking por caracteres fragmentou conceitos ou estruturas importantes?
*Sim.* Nos Testes 1, 2, 5 e 6, o corte por quantidade fixa de caracteres dividiu palavras ao meio e separou frases no meio de justificativas teóricas, quebrando o nexo conceitual do documento.

### 9. O chunking por parágrafo produziu chunks muito grandes?
Em alguns pontos específicos, sim. Embora a média tenha ficado em torno de 400 caracteres, parágrafos densos atingiram tamanhos maiores, o que pode poluir o contexto fornecido a um modelo de linguagem em sistemas RAG.

### 10. O chunking por sentença conseguiu preservar melhor o contexto?
*Sim.* O agrupamento de 3 sentenças (Teste 8) manteve unidades completas de pensamento (sujeito + verbo + predicado), evitando frases truncadas.

### 11. O Recursive Splitter apresentou vantagens?
*Sim.* O RecursiveCharacterTextSplitter (Teste 9) tentou primeiro manter parágrafos inteiros. Quando estes ultrapassavam o tamanho limite, ele recorria a quebras de linha e, em último caso, espaços. Isso uniu o controle de tamanho dos testes fixos com o respeito à estrutura da linguagem.

### 12. O Markdown Splitter conseguiu preservar a estrutura semântica?
*Sim, com excelência.* Ele organizou o documento diretamente pelos tópicos do índice, injetando o caminho da seção nos metadados do chunk.

### 13. Qual estratégia parece mais adequada para um sistema de RAG?
A combinação híbrida do *Teste 9 (Recursive Splitter)* com o *Teste 10 (Markdown Splitter)*. O Markdown Splitter preserva a hierarquia lógica nos metadados, e o Recursive garante que nenhuma seção isolada fique exageradamente grande.

### 14. Quais estratégias devem ser descartadas?
* *Teste 1 (200 caracteres):* Fragmenta excessivamente o texto e destrói o significado semântico.
* *Testes 1 a 4 (Character Splitter sem separadores naturais):* Cortam o texto de maneira mecânica sem considerar palavras ou parágrafos.

### 15. Quais estratégias devem ser utilizadas nos próximos experimentos?
Deve-se avançar utilizando *Recursive Character Splitting (Teste 9)* associado à extração de metadados por *Markdown (Teste 10)*, garantindo chunks de tamanho controlado com alta densidade semântica.

---

## 3. Conclusão Final

A escolha da melhor estratégia para RAG não deve se pautar apenas na contagem final de trechos. Para a garantia da qualidade da representação vetorial (embeddings), o *Recursive Splitter* e o *Markdown Splitter* apresentaram o equilíbrio ideal entre *respeito aos limites do texto, **integridade de estruturas* e *tamanho controlado dos blocos de contexto*.