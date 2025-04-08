import base64  # Utilizado para decodificar o conteúdo criptografado em base64
import json  # Para leitura do resultado em formato JSON
from cryptography.hazmat.primitives import serialization  # Para carregar a chave privada RSA
from cryptography.hazmat.primitives.asymmetric import padding  # Para definir o esquema de padding usado na descriptografia
from cryptography.hazmat.primitives import hashes  # Algoritmo de hash utilizado no padding OAEP

# Carrega a chave privada de um votante específico a partir de um arquivo PEM
def carregar_chave_privada(votante_id):
    caminho = f"chaves_privadas/privada_{votante_id}.pem"
    with open(caminho, "rb") as f:
        chave_privada = serialization.load_pem_private_key(f.read(), password=None)
    return chave_privada

# Descriptografa o resultado criptografado usando a chave privada do votante
def descriptografar_resultado(chave_privada, resultado_criptografado):
    try:
        dados = base64.b64decode(resultado_criptografado)  # Decodifica o texto base64
        resultado = chave_privada.decrypt(
            dados,
            padding.OAEP(  # Usa padding OAEP (padrão moderno e seguro para RSA)
                mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Máscara de geração baseada em SHA256
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return resultado.decode()  # Retorna o resultado descriptografado como string
    except Exception as e:
        print(f"⚠️ Erro ao descriptografar o resultado: {e}")
        return None

# Função principal que interage com o usuário e exibe o resultado
def main():
    votante_id = input("Digite seu ID para acessar o resultado: ")  # Solicita o ID do votante
    chave_privada = carregar_chave_privada(votante_id)  # Carrega a chave privada correspondente

    with open("resultado_votacao.json", "r") as f:  # Abre o arquivo de resultado
        conteudo = json.load(f)

    # Se o resultado não estiver criptografado, mostra diretamente
    if "resultado_criptografado" not in conteudo:
        print("❌ O arquivo não está criptografado. Exibição direta:")
        print(json.dumps(conteudo, indent=4, ensure_ascii=False))
        return

    resultado_criptografado = conteudo["resultado_criptografado"]
    resultado_descriptografado = descriptografar_resultado(chave_privada, resultado_criptografado)

    # Exibe o resultado descriptografado se bem-sucedido
    if resultado_descriptografado:
        print("\n✅ RESULTADO DA VOTAÇÃO:")
        print(resultado_descriptografado)

# Executa a função principal ao rodar o script diretamente
if __name__ == "__main__":
    main()
