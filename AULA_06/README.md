Escolher 2 cenários diferentes:

- Instrumentação Cirúrgica
- Radioamadorismo

| **Critério** | **Cenário 1: Instrumentação Cirúrgica** | **Cenário 2: Radioamadorismo** |
| --- | --- | --- |
| **Criticidade do Erro** | **Crítica (Zero tolerância a erro)**. Uma falha afeta a saúde/segurança do paciente. | **Baixa/Média**. Um erro causa descumprimento de norma de telecom ou erro de configuração de rádio. |
| **Perfil do Usuário** | Enfermeiro, instrumentador cirúrgico, residente médico (precisa de resposta rápida e cirúrgica). | Radioamador/hobbista técnico (busca consulta regulatória, tabelas e manuais de equipamentos). |
| **Natureza dos Dados** | Manuais de fabricantes (Stryker, Zimmer), POPs hospitalares, fotos e diagramas de caixas cirúrgicas. | Resoluções da ANATEL (ex: Res. 759), planos de faixas, manuais de transceptores (Icom, Yaesu), esquemas de antenas. |
| **Frequência de Atualização** | Média/Baixa (novos manuais de equipamentos ou atualizações de POPs). | Média (atualizações de normas da ANATEL ou adição de novos manuais de rádios). |

Parte 1 - Identificação dos problemas:

Cenário 1: Instrumentação Cirúrgica

1.1  Descrição do problema

- **Problema:** Dificuldade e demora na consulta manual a dezenas de catálogos de fornecedores e POPs (Procedimentos Operacionais Padrão) para conferência de caixas cirúrgicas, peças componentes e fluxos de esterilização antes da cirurgia.
- **Usuário:** Instrumentador Cirúrgico ou Técnico de Enfermagem de Bloco Cirúrgico. Acesso rápido via tablet/aplicativo web no centro cirúrgico ou expurgo.
- **Informação consultada:** Listas de peças de caixas cirúrgicas específicas, passos de desmontagem, tempos de autoclavação e compatibilidade de insumos.
- **Fonte dos dados:** PDFs de fabricantes e manuais de POP do hospital.
- **Por que não LLM puro:** O modelo base não conhece os procedimentos internos do hospital nem os manuais específicos de marcas comerciais. Além disso, LLM puro pode inventar ("alucinar") peças que não pertencem àquela caixa.

Três perguntas reais:

1. *"Quais pinças e componentes compõem a caixa de artroplastia total de joelho do fabricante X?"*
2. *"Qual é o tempo e temperatura de autoclave recomendados para a caneta de perfuração modelo Y?"*
3. *"Qual a sequência correta de limpeza e desmontagem do instrumental Z antes do expurgo?"*

1.2 Por que RAG?

- **Adequação:** Exige busca factual restrita a documentos privados e homologados pelo hospital.
- **Risco do LLM sem RAG:** O LLM poderia sugerir um processo de esterilização incorreto ou omitir uma peça crítica do kit, comprometendo a cirurgia.

1.3 Limitações - quando RAG não é a resposta?

- **Busca tradicional/SQL:** Se o usuário precisa saber *"Quantas caixas de joelho temos em estoque hoje no hospital?"*, RAG **não serve**. Isso exige consulta direta via SQL/API no sistema ERP do hospital.
- **Regras determinísticas:** A checagem de "validade da esterilização do pacote" deve ser feita por regra de sistema (Data Atual > Data de Validade), e não por IA.

Cenário 2: Radioamadorismo

1.1 Descrição do problema

- **Problema:** Complexidade para consultar rapidamente a legislação da ANATEL, atribuição de bandas por classe de operador (A, B ou C), modulações permitidas e configurações de rádios transceptores.
- **Usuário:** Radioamador (operação em estação fixa ou móvel), acessando por interface web ou CLI/API no computador do shack (estação).
- **Informação consultada:** Tabela de frequências por classe, potência máxima, regras de contest, manuais de rádios (Icom, Yaesu).
- **Fonte dos dados:** Resoluções da ANATEL em PDF/HTML, manuais de transceptores e guias de DX.
- **Por que não LLM puro:** O LLM confunde a legislação brasileira da ANATEL com a FCC dos EUA. Ele também erra detalhes técnicos de modelos específicos de rádios.

Três perguntas reais:

- *"Qual é o limite de potência máxima permitida para um radioamador Classe B operar na faixa de 40 metros?"*
- *"Quais são as sub-faixas destinadas exclusivamente para transmissão em CW na banda de 80m no Brasil?"*
- *"Como configurar a taxa de baud rate e o modo CI-V no rádio Icom IC-7300 para operação em FT8?"*

1.2 Por que RAG?

- **Adequação:** Permite grounding (ancoragem) direto na legislação local atualizada e manuais técnicos do fabricante sem retreinar o modelo.
- **Risco do LLM sem RAG:** Responder com o plano de faixas americano (FCC), levando o operador a transmitir em frequência não autorizada pela ANATEL (infração regulatória).

1.3 Limitações - Quando o RAG não é resposta?

- **Contar / Sumarizar quantitativo:** Para perguntas como *"Quantos contatos (QSOs) eu fiz no mês de julho?"*, RAG responde mal. O correto é um banco de dados relacional fazendo um `COUNT(*)` no arquivo ADIF/Logbook.
- **Uso direto de API:** Para consultar propagação solar em tempo real (SFI, K-index), o sistema deve chamar uma API direta (ex: NOAA/Solar Data) em vez de buscar em documentos indexados.

Parte 2 - Organização dos documentos

Cenário 1: Instrumentação Cirúrgica

Estrutura de pastas proposta:

documentos/
├── manuais_fabricantes/     (PDFs técnicos de Stryker, Zimmer, etc.)
├── pop_hospital/            (Procedimentos Operacionais Padrão internos)
└── listas_verificacao/      (Composição exata de cada caixa cirúrgica)

- **Justificativa da estrutura:** Separar a fonte da verdade interna (POPs e Listas) dos manuais externos dos fabricantes facilita a filtragem rápida por tipo de documento ou por especialidade/fornecedor.
- **O que NÃO entra na base:** Dados confidenciais de pacientes (prontuários, nomes, CPFs) e históricos de cirurgias. Apenas documentação técnica e institucional.
- **Gestão de Versões:**
    - Se o POP do hospital for atualizado em 2026, a versão de 2024 é alterada no metadado para `status: "obsoleto"` ou removida/arquivada da base ativa.
    - O metadado `version` e `is_active: true/false` garante que o RAG só consulte a versão vigente, evitando que a IA recomende uma higienização que caducou.
    
    Cenário 2: Radioamadorismo
    
    Estrutura de pasta proposta:
    
    documentos/
    ├── anatel_regulamentacao/   (Resoluções, Planos de Faixas, Atribuições)
    ├── manuais_equipamentos/    (Manual do usuário, esquemas de Icom, Yaesu)
    └── guias_modos_digitais/    (Guias de FT8, CW, Antenas e Software)
    
    - **Justificativa da estrutura:** Reflete o modelo mental do operador. Ele pesquisa ou sobre a **lei/regra** (ANATEL) ou sobre o **equipamento/hardware** (Manuais) ou sobre **procedimento prático** (Guias).
    - **O que NÃO entra na base:** Logs pessoais de contatos (arquivos .ADI ou logs de contest) — isso deve ir para um banco relacional/SQL.
    - **Gestão de Versões:** Quando a ANATEL lança uma nova resolução substituindo uma antiga, a nova entra na pasta com metadado atualizado e a antiga é marcada como `deprecated` para não gerar conflito normativo no retrieval.
    
    Parte 3 - Pipeline de Ingestão
    
    Aqui detalhei a transformação dos arquivos originais em informação pesquisável.
    
    Documentos ➔ Extração ➔ Limpeza / Normalização ➔ Metadados ➔ Chunking ➔ Embeddings ➔ Banco Vetorial
    
    3.1 Extração
    
    | **Aspecto** | **Cenário 1: Instrumentação Cirúrgica** | **Cenário 2: Radioamadorismo** |
    | --- | --- | --- |
    | **PDFs com texto selecionável** | Extração com bibliotecas diretas (ex: PyPDF / pdfplumber). | Extração direta com PyPDF / pdfplumber. |
    | **PDFs digitalizados (Scans)** | Ocorre em manuais antigos. Aplicação obrigatória de **OCR** (Tesseract / EasyOCR). | Ocorre em diagramas e manuais antigos de rádios dos anos 80. Requer OCR. |
    | **Tabelas** | **Crítico!** A composição de caixas é 100% em tabelas. Deve-se converter tabelas para Markdown/HTML ou JSON estruturado para preservar colunas (peça, quantidade, tamanho). | Importante para tabelas de frequência/potência. Converter em tabelas Markdown para manter a relação coluna-linha. |
    | **Imagens / Diagramas** | Diagramas de montagem de peças requerem descrição textual multimodal (Image Captioning via LLM) ou descarte se for apenas ilustrativo. | Esquemas elétricos de antenas: preservar legenda e texto descritivo associado. |

3.3 Limpeza e Normalização

- **O que remover:**
    - **Ambos os cenários:** Cabeçalhos e rodapés repetidos em todas as páginas (ex: "Hospital X - Página 12 de 50"), marcas d'água ("CONFIDENCIAL"), números de páginas e quebras de linha estrambóticas.
- **O que padronizar:**
    - Codificação (UTF-8), acentuação, e unificação de termos técnicos (ex: em rádio, padronizar "7 MHz" e "40 metros"; em cirurgia, padronizar nomes de instrumentos).
- **Risco de limpar demais:**
    - Se remover tabelas ou notas de rodapé pequenas que continham alertas de segurança (ex: *"Atenção: Não nocivo se autoclavado a 121°C"*), o RAG perde a instrução de segurança mais importante.
    
    3.3 Frequência de Ingestão
    
    - **Cenário 1 (Instrumentação Cirúrgica):**
        - **Frequência:** Batch/Agendado (Semanal) ou sob demanda (quando o setor de Qualidade lança um novo POP ou adquire um novo equipamento).
        - **Reprocessamento:** Reprocessa-se **apenas o documento criado ou alterado** identificando via Hash/ID do arquivo, sem recriar o banco inteiro.
    - **Cenário 2 (Radioamadorismo):**
        - **Frequência:** Eventual/Sob demanda (quando a ANATEL publica nova resolução no Diário Oficial ou o usuário adiciona um manual do seu rádio novo).
        - **Reprocessamento:** Reprocessamento pontual do documento modificado.
        
        Parte 4 - Metadados
        
        Metadados que seriam aramazenados.
        
        Metadados são cruciais para filtrar as buscas antes e depois da recuperação vetorial( pre-filtering/ pos-filtering).
        
        4.1 Shema de Metadados
        
        Cenário 1: Instrumentação Cirúrgica
        
        JSON
        
        {
        "document_id": "doc-pop-084",
        "chunk_id": "doc-pop-084-chk-02",
        "title": "POP Esterilização de Instrumental de Ortopedia",
        "source": "pop_hospital/ortopedia/pop_084.pdf",
        "document_type": "pop",
        "specialty": "ortopedia",
        "manufacturer": "Stryker",
        "version": "2.1",
        "is_active": true,
        "created_at": "2025-10-15",
        "page": 4,
        "section": "LAVAGEM E ULTRA-SOM"
        }
        
        Por que esses metadados?
        
        - `specialty` e `manufacturer`: Permitem filtrar as perguntas direto na especialidade ou marca (ex: buscar apenas caixas da *Stryker* de *ortopedia*).
        - `is_active` / `version`: Impedem a leitura de normas revogadas.
        - `page` / `section`: Permitem citar exatamente em qual página e seção do POP a regra está.
        
        Cenário 2: Radioamadorismo
        
        JSON
        
        {
        "document_id": "doc-anatel-res759",
        "chunk_id": "doc-anatel-res759-chk-15",
        "title": "Resolução ANATEL nº 759/2023 - Regulamento do Service de Radioamador",
        "source": "anatel_regulamentacao/res_759.pdf",
        "document_type": "resolucao",
        "category": "regulamentacao",
        "operator_class": "Classe B",
        "band": "40m",
        "equipment_model": "geral",
        "created_at": "2023-05-10",
        "page": 12,
        "section": "Atribuição de Frequências"
        }
        
        Por que esses metadados?
        
        - `operator_class`: Filtra as regras vigentes apenas para a classe do operador (Classe A, B ou C).
        - `band`: Filtra trechos de documento referentes a uma faixa específica (ex: 40m, 80m, 2m).
        - `equipment_model`: Associa o trecho ao modelo correto do rádio quando a busca é técnica.
        
        4.2 Metadados do Chunk
        
        4.2 Questões de Metadados
        
        Metadado indispensável para filtrar a busca:
        
        - **Cenário 1:** `specialty` ou `is_active`. Exemplo: *"Exibir apenas procedimentos ativos de Ortopedia"*.
        - **Cenário 2:** `operator_class` ou `band`. Exemplo: *"O que a Classe C pode operar na faixa de 10m?"* (Se não filtrar por Classe C, a IA pode retornar regras válidas apenas para Classe A).
        
        Metadado para citar a fonte na resposta:
        
        Nome do documento (`title`), página (`page`) e seção (`section`). Exemplo de citação exibida na tela: `[Fonte: POP 084 - Ortopedia, Pág. 4, Seção: Lavagem]`.
        
        Qual metadado para seria caríssimo para acrescentar depois?
        
        Metadados extraídos do conteúdo que exigem reprocessamento via LLM (ex: `specialty`, `operator_class`, `equipment_model`). Se a base já tiver milhares de chunks e você decidir criar esses filtros semanticamente depois, terá que rodar o pipeline de extração por LLM novamente para todos os chunks antigos.
        
        Parte 5 - Chunking / Splitting
        
        Divisão dos documentos em pedaços pesquisáveis.
        
        | **Parâmetro** | **Cenário 1: Instrumentação Cirúrgica** | **Cenário 2: Radioamadorismo** |  |
        | --- | --- | --- | --- |
        | **Estratégia** | **Chunking Baseado em Estrutura / Markdown** (Headers + Tabelas completas). | **Chunking Hierárquico / Recursivo por Caracteres** respeitando parágrafos e artigos. |  |
        | **Tamanho do Chunk** | ~500 a 800 tokens (médio/pequeno para manter contexto exato da instrução). | ~800 a 1000 tokens (maior, para capturar artigos de leis ou instruções de configuração inteiras). |  |
        | **Overlap (Sobreposição)** | 100 a 150 tokens (~15%). | 150 a 200 tokens (~20%). |  |
        | **Justificativa do Overlap** | Evita que uma lista de instrumental ou um passo a passo cirúrgico seja cortado no meio de uma frase crítica. | Preserva o contexto entre caput de artigo, incisos e parágrafos de resoluções legais. |  |
        |  |  |  |  |
        |  |  |  |  |

  Tratamento de Tabelas:

As tabelas são convertidas para formato **Markdown** e mantidas **inteiras dentro de um único chunk** (se couberem). Cortar uma tabela de componentes cirúrgicos ao meio inutiliza a consulta.

O que acontece se o chunk for muito pequeno?

Perde-se o contexto (ex: o chunk traz "Temperatura: 134°C" sem mencionar a qual equipamento ou processo se refere).

O que acontece se o chunk for muito grande?

O retrieval fica diluído/ruidoso. O modelo de embeddings perde precisão e atinge o limite de contexto (*context window*) com menos trechos relevantes.

Parte 6 - Embeddings

| **Item** | **Cenário 1: Instrumentação Cirúrgica** | **Cenário 2: Radioamadorismo** |
| --- | --- | --- |
| **Modelo Escolhido** | `text-embedding-3-large` (OpenAI) ou `multilingual-e5-large` (Local) | `text-embedding-3-small` (OpenAI) ou `bge-m3` (OpenSource) |
| **Dimensão** | 1536 ou 3072 | 1536 ou 1024 |
| **Suporta Português?** | Sim (Multilíngue) | Sim (Multilíngue) |
| **É Open Source?** | Depende da escolha (`text-embedding-3` = Proprietário; `e5`/`bge-m3` = Open Source). | Ídem. |
| **Execução Local/API** | **Local (Recomendado/Obrigatório se sigiloso)** para garantir privacidade hospitalar (LGPD). | **API** (Redução de custo e baixa sensibilidade de dados). |
| **Custo Aproximado** | Baixo ($0,02 - $0,13 por milhão de tokens na API; ou R$ 0 em infra própria). | Baixo. |

Justificativa de Escolha:

- **Cenário 1:** Exige alta precisão em termos técnicos e médicos em português. Se houver restrição rígida de privacidade no hospital, usa-se modelo open source local (ex: `multilingual-e5-large`).
- **Cenário 2:** Prioriza custo-benefício e excelente suporte a termos técnicos e acrônimos em inglês e português (CW, FT8, SSB, ANATEL).

Arquitetura Final

[ 1. FONTES DE DADOS ]
• PDFs de POPs do Hospital
• Manuais de Fabricantes (Storz/Stryker)
• Resoluções da ANATEL (Res. 759)
│
▼
[ 2. TRATAMENTO & INGESTÃO ]
• Extração de Texto (PyPDF / Tesseract OCR)
• Conversão de Tabelas ➔ Markdown
• Limpeza de Cabeçalhos e Dicionário de Sinônimos
│
▼
[ 3. PROCESSAMENTO ]
• Chunking (Divisão em trechos contextuais)
• Geração de Metadados (JSON)
• Transformação em Vetores (Modelo de Embedding)
│
▼
[ 4. ARMAZENAMENTO ]
• Banco de Dados Vetorial (Vector DB - Chroma/Qdrant/Pinecone)
│
▼
[ 5. BUSCA & RECUPERAÇÃO (RETRIEVAL) ]
• Pergunta do Usuário ➔ Vetorização da Pergunta
• Busca por Similaridade Cóseno + Filtro de Metadados
• Recuperação dos Top-K Chunks Relevantes
│
▼
[ 6. GERAÇÃO & CONSUMO ]
• Prompt Enriquecido (Pergunta + Chunks Recorridos) ➔ LLM
• Resposta com Citação da Fonte
• Interface do Usuário (Chatbot / App Web no Hospital/Shack)

### Detalhamento das Etapas do Fluxo

1. **Origem dos Documentos (Data Sources):**
    - **Cenário 1:** Arquivos PDF não estruturados com os Procedimentos Operacionais Padrão (POPs) de montagem de caixas de Histerectomia e manuais em PDF dos fabricantes de instrumental.
    - **Cenário 2:** Documentos regulatórios em PDF baixados da ANATEL e guias técnicos de operação em modos digitais.
2. **Tratamento dos Dados (Data Preprocessing):**
    - **Extração:** Extração do texto bruto via `pdfplumber` e aplicação de OCR (EasyOCR) para documentos escaneados ou diagramas de caixas.
    - **Estruturação:** Transformação de tabelas de componentes em formato **Markdown** para não perder a relação entre linhas e colunas.
    - **Normalização:** Aplicação de dicionário de termos de bancada (para mapear sinônimos da prática médica/radioamadorismo).
3. **Processamento (Processing & Indexing):**
    - **Chunking:** Quebra do texto em pedaços menores (de 600 a 900 tokens) mantendo a integridade de parágrafos e tabelas.
    - **Metadados:** Anexação de tags (`specialty`, `is_active`, `band`, `allowed_classes`) a cada chunk.
    - **Embeddings:** Conversão dos chunks de texto em vetores numéricos através do modelo de embedding.
4. **Busca e Recuperação (Retrieval):**
    - Quando o usuário faz uma pergunta, a pergunta é transformada no mesmo espaço vetorial.
    - O sistema realiza uma **Busca Híbrida**: filtra primeiro pelos metadados (ex: apenas a banda de 40m ou apenas caixas ativas) e depois calcula a similaridade vetorial para encontrar as trechos mais relevantes.
5. **Consumo pelo Usuário (User Layer):**
    - O LLM recebe a pergunta original junto com os trechos recuperados (*context argumentation*) e gera a resposta final.
    - A resposta é exibida em uma interface amigável (Interface Web ou App Mobile) contendo a resposta direta e a citação da fonte original do documento para conferência.

Comparação entre os dois cenário

| Critério | Cenário 1: Instrumentação Cirúrgica | Cenário 2: Radioamadorismo |
| --- | --- | --- |
| **Criticidade do Erro** | **Crítica (Zero tolerância a erro):** Uma falha compromete a segurança cirúrgica e a saúde do paciente. | **Baixa/Média:** Erros geram apenas dúvidas técnicas sobre frequências ou operação. |
| **Privacidade e Hospedagem** | **On-Premise / Local:** Exige conformidade rigorosa com LGPD e sigilo de dados hospitalares. | **Nuvem / API Pública:** Dados regulatórios (ANATEL) e manuais de público domínio. |
| **Estratégia de Chunking** | **Chunks Menores (~600 tokens):** Garante precisão na contagem e especificação exata de itens cirúrgicos. | **Chunks Maiores (~900 tokens):** Preserva o contexto completo de artigos de leis e manuais. |
| **Metadados Chave** | `especialidade`, `fabricante`, `nome_caixa`, `status_ativo` | `frequencia`, `banda`, `classe_licenca`, `norma_anatel` |
| **Modelo de Embedding** | `text-embedding-3-large` (ou `e5-large` local): Alta precisão para vocabulário médico. | `text-embedding-3-small`: Foco em baixo custo e eficiência para textos regulatórios. |

---

Em que pontos as decisões foram diferentes? Por quê?

- *Diferença:* O Cenário 1 (Hospital) usou processamento local e chunks menores para proteger dados (LGPD) e garantir precisão em listas de instrumentos. O Cenário 2 (Radioamadorismo) usou APIs na nuvem e chunks maiores para economizar custos e manter artigos de leis inteiros.
    
    Em que pontos foram iguais? Isso é sinal de boa prática geral ou de você ter repetido a decisão sem pensar?
    
    *Igualdade:* Ambas usaram conversão de tabelas para Markdown e filtragem por metadados. Isso é **boa prática de IA**, pois modelos de embedding perdem contexto em PDFs brutos e precisam de metadados para evitar buscas erradas.
    
    Se você tivesse que construir apenas um dos dois, qual escolheria, e por quê?
    
    - *Escolha:* Cenário 1 (Cirúrgico), pois possui maior valor agregado, alto impacto na segurança dos pacientes e exige tolerância zero a erros da IA.
    - **Riscos e Limitações:**
        - Falhas de OCR em papéis escaneados velhos e custo de manter servidores com GPU local no hospital.