import os
import json
from seguranca_arquivos import carregar_chave_aes, descriptografar_arquivos_sensitiveis

# Função principal que executa o processo de visualização segura do resultado
def main():
    # Solicita o ID do votante para localizar o arquivo certo e carregar a chave correta
    votante_id = input("🆔 Digite seu ID para acessar o resultado: ")
    caminho_criptografado = f"resultado_votacao_{votante_id}.json.enc"

    # Verifica se o arquivo criptografado existe
    if not os.path.exists(caminho_criptografado):
        print(f"❌ Arquivo '{caminho_criptografado}' não encontrado.")
        return

    try:
        # Carrega a chave AES do votante, descriptografando com RSA
        print("🔐 Carregando chave AES para descriptografar o resultado...")
        chave_aes = carregar_chave_aes(votante_id)

        # Descriptografa o arquivo JSON do resultado
        print("🛠️ Descriptografando o resultado da votação...")
        descriptografar_arquivos_sensitiveis(caminho_criptografado, chave_aes)

        # Lê o conteúdo descriptografado
        caminho_descriptografado = caminho_criptografado.replace(".enc", "")
        with open(caminho_descriptografado, "r", encoding="utf-8") as f:
            resultado = json.load(f)

        # Exibe o conteúdo de forma formatada
        print("\n✅ RESULTADO DA VOTAÇÃO:")
        print(json.dumps(resultado, indent=4, ensure_ascii=False))

        # Remove o arquivo JSON descriptografado após leitura, por segurança
        os.remove(caminho_descriptografado)
        print("🧹 Arquivo descriptografado temporário removido.")

    except Exception as e:
        print(f"⚠️ Erro ao acessar ou descriptografar o resultado: {e}")

# Executa o main se o script for rodado diretamente
if __name__ == "__main__":
    main()
