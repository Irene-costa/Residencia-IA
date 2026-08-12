from langchain_core.documents import Document

# 1. Criando a lista com pelo menos 5 objetos Document
documentos = [
    Document(
        page_content="Embeddings são representações vetoriais densas de texto.",
        metadata={
            "fonte": "arquivo_01.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "embeddings",
            "autor": "Seu Nome"
        }
    ),
    Document(
        page_content="Chunking consiste em dividir textos longos em partes menores.",
        metadata={
            "fonte": "arquivo_01.md",
            "pagina": 2,
            "tipo": "pratica",
            "tema": "chunking",
            "autor": "Seu Nome"
        }
    ),
    Document(
        page_content="RAG combina busca de informação com geração de texto por LLM.",
        metadata={
            "fonte": "arquivo_02.md",
            "pagina": 1,
            "tipo": "teoria",
            "tema": "RAG",
            "autor": "Seu Nome"
        }
    ),
    Document(
        page_content="Tokenização é o processo de dividir um texto em unidades chamadas tokens.",
        metadata={
            "fonte": "arquivo_02.md",
            "pagina": 3,
            "tipo": "teoria",
            "tema": "tokenização",
            "autor": "Seu Nome"
        }
    ),
    Document(
        page_content="A busca vetorial encontra textos similares usando a distância entre embeddings.",
        metadata={
            "fonte": "arquivo_03.md",
            "pagina": 5,
            "tipo": "pratica",
            "tema": "embeddings",
            "autor": "Seu Nome"
        }
    )
]

# 2. Exibindo o conteúdo (page_content) e os metadados de cada documento
print("=== DETALHES DOS DOCUMENTOS ===")
for i, doc in enumerate(documentos, 1):
    print(f"\nDocumento {i}:")
    print(f"Conteúdo: {doc.page_content}")
    print(f"Metadados: {doc.metadata}")

# 3. Exibindo o resultado de len(documentos)
print("\n===============================")
print(f"Total de documentos criados: {len(documentos)}")

# ==========================================
# RESPOSTA ÀS PERGUNTAS DA ATIVIDADE
# ==========================================

# Teste 1: Tipos de dados aceitos em metadata (Listas e Dicionários aninhados)
print("\n--- Teste 1: Metadados complexos ---")
doc_complexo = Document(
    page_content="Texto sobre testes de metadados.",
    metadata={
        "tags": ["ia", "python", "rag"],
        "detalhes": {"revisado": True, "versao": 1.0}
    }
)
print("Metadata com lista e dicionário aninhado:")
print(doc_complexo.metadata)


# Teste 2: Criando Document sem passar o parâmetro metadata
print("\n--- Teste 2: Documento sem metadata ---")
doc_sem_meta = Document(page_content="Texto sem passar metadados no construtor.")
print(f"Resultado do metadata: {doc_sem_meta.metadata}")