import os
from pathlib import Path

# Desativa otimizações de compilação do PyTorch para economizar RAM
os.environ["TORCH_COMPILE_DISABLE"] = "1"

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# Aponta para a pasta AULA_02
PASTA_AULA = Path("AULA_02")

# Configura o Docling para rodar em modo leve (CPU)
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False  # Desativa OCR pesado para evitar estouro de memória
pipeline_options.do_table_structure = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# Busca os arquivos PDF dentro de AULA_02
arquivos_pdf = list(PASTA_AULA.glob("*.pdf"))

if not arquivos_pdf:
    print(f"Nenhum arquivo PDF foi encontrado dentro da pasta '{PASTA_AULA}'.")
else:
    for arquivo_pdf in arquivos_pdf:
        print(f"Convertendo: {arquivo_pdf.name}...")
        try:
            result = converter.convert(arquivo_pdf)
            markdown_content = result.document.export_to_markdown()
            
            # Salva o arquivo .md dentro da mesma pasta
            arquivo_md = arquivo_pdf.with_suffix(".md")
            with open(arquivo_md, "w", encoding="utf-8") as f:
                f.write(markdown_content)
                
            print(f"-> Sucesso: {arquivo_md.name}")
        except Exception as e:
            print(f"-> Erro ao converter {arquivo_pdf.name}: {e}")

print("\nProcessamento concluído!")