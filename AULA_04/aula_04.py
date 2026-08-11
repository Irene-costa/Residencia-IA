import os
import re
import json
import shutil
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)

# 1. Carregamento do Modelo de Embedding
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
print(f"Carregando modelo de embedding: {EMBEDDING_MODEL}...")
embedder = SentenceTransformer(EMBEDDING_MODEL)

pasta_entrada = "."
pasta_results = "results"
os.makedirs(pasta_results, exist_ok=True)

# Lista apenas os arquivos Markdown dos artigos
arquivos_md = sorted([f for f in os.listdir(pasta_entrada) if f.endswith(".md") and not f.startswith("relatorio")])

# 2. Definição dos 10 Testes de Chunking
def rodar_testes(texto):
    testes = {}
    testes[1] = ("fixed", 200, 0, CharacterTextSplitter(chunk_size=200, chunk_overlap=0, separator="").split_text(texto), {})
    testes[2] = ("fixed", 500, 0, CharacterTextSplitter(chunk_size=500, chunk_overlap=0, separator="").split_text(texto), {})
    testes[3] = ("fixed", 1000, 0, CharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separator="").split_text(texto), {})
    testes[4] = ("fixed", 2000, 0, CharacterTextSplitter(chunk_size=2000, chunk_overlap=0, separator="").split_text(texto), {})
    testes[5] = ("fixed_with_overlap", 500, 50, CharacterTextSplitter(chunk_size=500, chunk_overlap=50, separator="").split_text(texto), {})
    testes[6] = ("fixed_with_overlap", 500, 200, CharacterTextSplitter(chunk_size=500, chunk_overlap=200, separator="").split_text(texto), {})
    
    chunks_p = [p.strip() for p in texto.split("\n\n") if p.strip()]
    testes[7] = ("by_paragraph", None, None, chunks_p, {"unit": "paragraph"})
    
    sentencas = re.split(r'(?<=[.!?])\s+', texto.replace("\n", " "))
    chunks_s = [" ".join(sentencas[i:i+3]).strip() for i in range(0, len(sentencas), 3) if " ".join(sentencas[i:i+3]).strip()]
    testes[8] = ("grouped_sentences", None, None, chunks_s, {"grouped_sentences": 3})
    
    sp9 = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", " ", ""])
    testes[9] = ("recursive", 500, 50, sp9.split_text(texto), {"separators": ["\\n\\n", "\\n", " ", ""]})
    
    headers = [("#", "header_1"), ("##", "header_2"), ("###", "header_3")]
    docs_md = MarkdownHeaderTextSplitter(headers_to_split_on=headers).split_text(texto)
    testes[10] = ("markdown_structure", None, None, [d.page_content for d in docs_md], [d.metadata for d in docs_md])
    
    return testes

resumo_global = {}

# 3. Loop de Processamento mantendo a árvore exata do Notion
for idx_doc, nome_arquivo in enumerate(arquivos_md, start=1):
    doc_folder_name = f"documento_{idx_doc:02d}"
    caminho_doc_origem = os.path.join(pasta_entrada, nome_arquivo)
    
    # Criar subpasta results/documento_XX/markdown/
    pasta_doc = os.path.join(pasta_results, doc_folder_name)
    pasta_markdown = os.path.join(pasta_doc, "markdown")
    os.makedirs(pasta_markdown, exist_ok=True)
    
    # Copia o arquivo .md para a subpasta markdown/
    shutil.copy(caminho_doc_origem, os.path.join(pasta_markdown, f"{doc_folder_name}.md"))
    
    with open(caminho_doc_origem, "r", encoding="utf-8", errors="ignore") as f:
        texto_conteudo = f.read()

    print(f"Processando [{doc_folder_name}]: {nome_arquivo}...")
    testes_executados = rodar_testes(texto_conteudo)
    experimentos_resumo = []

    for test_id, (strategy, chunk_size, chunk_overlap, chunks, meta_info) in testes_executados.items():
        embeddings = embedder.encode(chunks, show_progress_bar=False).tolist() if chunks else []
        dim_embedding = len(embeddings[0]) if embeddings else 0
        avg_size = round(sum(len(c) for c in chunks) / len(chunks), 1) if chunks else 0.0

        res_item = {
            "test_id": test_id,
            "strategy": strategy,
            "chunk_size": chunk_size if chunk_size is not None else 0,
            "chunk_overlap": chunk_overlap if chunk_overlap is not None else 0,
            "num_chunks": len(chunks),
            "avg_chunk_size": avg_size,
            "embedding_dimension": dim_embedding
        }
        experimentos_resumo.append(res_item)

        lista_json_chunks = []
        for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings), start=1):
            chunk_metadata = meta_info[idx - 1] if isinstance(meta_info, list) and idx <= len(meta_info) else (meta_info if isinstance(meta_info, dict) else {})
            lista_json_chunks.append({
                "chunk_id": f"{doc_folder_name}_test{test_id:02d}_chunk{idx:03d}",
                "document_id": doc_folder_name,
                "document_name": nome_arquivo,
                "test_id": test_id,
                "strategy": strategy,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "text": chunk_text,
                "embedding": emb,
                "metadata": chunk_metadata
            })

        # Criar pasta test_XX/
        pasta_teste = os.path.join(pasta_doc, f"test_{test_id:02d}")
        os.makedirs(pasta_teste, exist_ok=True)
        with open(os.path.join(pasta_teste, "chunks_embeddings.json"), "w", encoding="utf-8") as f_out:
            json.dump(lista_json_chunks, f_out, ensure_ascii=False, indent=2)

    resumo_global[doc_folder_name] = {
        "original_file": nome_arquivo,
        "experiments": experimentos_resumo
    }

# 4. Salva o summary.json na raiz de results/
with open(os.path.join(pasta_results, "summary.json"), "w", encoding="utf-8") as f_sum:
    json.dump(resumo_global, f_sum, ensure_ascii=False, indent=2)

print("\nProcessamento finalizado! Estrutura idêntica à do Notion gerada em 'results/'.")