import os
from pypdf import PdfReader

pasta = "."

# Procura todos os PDFs na pasta AULA_04
arquivos_pdf = [f for f in os.listdir(pasta) if f.endswith(".pdf")]

print(f"Encontrados {len(arquivos_pdf)} arquivos PDF para conversão...\n")

for arquivo in arquivos_pdf:
    caminho_pdf = os.path.join(pasta, arquivo)
    reader = PdfReader(caminho_pdf)
    
    conteudo_md = [f"# {arquivo.replace('.pdf', '').replace('_', ' ').title()}\n"]
    
    for i, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text()
        if texto:
            conteudo_md.append(f"## Página {i}\n\n{texto.strip()}")
            
    # Salva com a extensão .md
    nome_md = arquivo.replace(".pdf", ".md")
    caminho_md = os.path.join(pasta, nome_md)
    
    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write("\n\n".join(conteudo_md))
        
    print(f"✅ Convertido: {arquivo} ➔ {nome_md}")

print("\n🎉 Conversão concluída! Todos os PDFs foram transformados em Markdown (.md).")