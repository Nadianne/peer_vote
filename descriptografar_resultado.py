import os
import json
import sys
from seguranca_arquivos import descriptografar_arquivos_sensitiveis, carregar_chave_aes

# Função para descriptografar o arquivo de um votante específico
def descriptografar_arquivo_votante(votante_id):
    # Caminho do arquivo criptografado do votante
    caminho_arquivo = f"votos/votos_{votante_id}.txt.enc"

    # Verifica se o arquivo criptografado existe
    if not os.path.exists(caminho_arquivo):
        print(f"[⚠️] Arquivo '{caminho_arquivo}' não encontrado.")
        return

    # Carrega a chave AES do votante (descriptografada com a chave privada RSA)
    chave_aes = carregar_chave_aes(votante_id)

    # Descriptografa o arquivo usando a chave AES
    descriptografar_arquivos_sensitiveis(caminho_arquivo, chave_aes)

# Verifica se o ID do votante foi passado como argumento no terminal
if len(sys.argv) < 2:
    print("Uso: python descriptografar_resultado.py <id_do_votante>")
    sys.exit(1)

# Captura o ID do votante a partir dos argumentos
votante = sys.argv[1]

# Garante que o ID do votante não está vazio
if not votante:
    print("[⚠️] ID do votante não pode ser vazio.")
    sys.exit(1)

# Tenta descriptografar o arquivo associado ao votante
try:
    descriptografar_arquivo_votante(votante)
    print(f"[✅] Descriptografia concluída para o votante '{votante}'.")
except Exception as e:
    print(f"[⚠️] Ocorreu um erro ao tentar descriptografar o arquivo para o votante '{votante}': {str(e)}")
    sys.exit(1)
