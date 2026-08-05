import os
import json
from pathlib import Path
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# 1. Definir a estrutura exata do JSON esperada
class MetadadosArtigo(BaseModel):
    titulo: str = Field(description="Título principal do artigo")
    autores: list[str] = Field(description="Lista com os nomes dos autores")
    ano: int = Field(description="Ano de publicação do artigo (ex: 2024)")

# 2. Inicializar o cliente do Groq com a sua chave de API
# Coloque a sua chave da Groq na aspas abaixo (ex: "gsk_...")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def extrair_metadados(caminho_arquivo: str) -> dict:
    """
    Lê o conteúdo de um arquivo .md e extrai os metadados em formato JSON estruturado.
    """
    path = Path(caminho_arquivo)
    
    with open(path, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Prompt instruindo o modelo a responder estritamente no esquema JSON do Pydantic
    schema_json = json.dumps(MetadadosArtigo.model_json_schema(), ensure_ascii=False)
    
    prompt_sistema = f"""
    Você é um assistente especializado em extrair metadados de artigos acadêmicos.
    Extraia as informações do texto e responda OBRIGATORIAMENTE em formato JSON válido seguindo este esquema:
    {schema_json}
    """

    # Chamada para a API do Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Modelo rápido e preciso da Groq
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Extraia os metadados do seguinte texto:\n\n{conteudo[:3000]}"}
        ],
        response_format={"type": "json_object"}
    )

    # Converte o texto retornado em dicionário Python
    resultado = json.loads(response.choices[0].message.content)
    return resultado


# Execução para testar em todos os arquivos da pasta AULA_02
if __name__ == "__main__":
    pasta_aula = Path("AULA_02")
    arquivos_md = list(pasta_aula.glob("*.md"))

    if not arquivos_md:
        print(f"Nenhum arquivo .md encontrado na pasta {pasta_aula}")
    else:
        for arquivo in arquivos_md:
            print(f"\n==========================================")
            print(f"Processando: {arquivo.name}")
            print(f"==========================================")
            
            try:
                metadados = extrair_metadados(str(arquivo))
                
                # Define o nome do arquivo .json
                arquivo_json = arquivo.with_suffix(".json")
                
                # Salva o arquivo .json na pasta AULA_02
                with open(arquivo_json, "w", encoding="utf-8") as f:
                    json.dump(metadados, f, ensure_ascii=False, indent=2)
                    
                print(f"-> Salvo com sucesso: {arquivo_json.name}")
            except Exception as e:
                print(f"Erro ao processar {arquivo.name}: {e}")

    print("\nTodos os arquivos JSON foram gerados com sucesso!")