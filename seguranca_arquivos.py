# Importa módulos essenciais
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # AES
from cryptography.hazmat.primitives import serialization, hashes              # Para RSA
from cryptography.hazmat.primitives.asymmetric import padding                 # Para RSA

# 🔐 Gera uma chave AES-256 (32 bytes aleatórios)
def gerar_chave_aes():
    return os.urandom(32)

# 🔐 Salva a chave AES criptografada com a chave pública do votante
def salvar_chave_aes(chave_aes, votante_id):
    caminho_publica = f"chaves_publicas/publica_{votante_id}.pem"
    caminho_chave_aes = f"chaves_simetricas/chave_simetrica_{votante_id}.key"

    # Carrega a chave pública do votante
    with open(caminho_publica, "rb") as f:
        chave_publica = serialization.load_pem_public_key(f.read())

    # Criptografa a chave AES com a chave pública
    chave_aes_criptografada = chave_publica.encrypt(
        chave_aes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Salva a chave AES criptografada em disco
    with open(caminho_chave_aes, "wb") as f:
        f.write(chave_aes_criptografada)

# 🔐 Carrega e descriptografa a chave AES usando a chave privada do votante
def carregar_chave_aes(votante_id):
    caminho_privada = f"chaves_privadas/privada_{votante_id}.pem"
    caminho_chave_aes = f"chaves_simetricas/chave_simetrica_{votante_id}.key"

    # Carrega a chave privada do votante
    with open(caminho_privada, "rb") as f:
        chave_privada = serialization.load_pem_private_key(f.read(), password=None)

    # Carrega a chave AES criptografada
    with open(caminho_chave_aes, "rb") as f:
        chave_aes_criptografada = f.read()

    # Descriptografa a chave AES com a chave privada
    chave_aes = chave_privada.decrypt(
        chave_aes_criptografada,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return chave_aes

# 🔐 Criptografa o conteúdo de um arquivo com AES e remove o original
def criptografar_arquivo(caminho_entrada, chave_aes):
    if not os.path.exists(caminho_entrada):
        return

    with open(caminho_entrada, "rb") as f:
        dados = f.read()

    # Gera IV (vetor de inicialização) e configura cifra AES-CBC
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(chave_aes), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Aplica padding manual (PKCS7 simplificado)
    padding_len = 16 - len(dados) % 16
    dados += bytes([padding_len]) * padding_len

    dados_criptografados = iv + encryptor.update(dados) + encryptor.finalize()

    # Salva arquivo criptografado e remove o original
    caminho_saida = caminho_entrada + ".enc"
    with open(caminho_saida, "wb") as f:
        f.write(dados_criptografados)

    os.remove(caminho_entrada)
    print(f"[🔐] Arquivo criptografado: {caminho_saida}")

# 🔓 Descriptografa arquivos AES (com IV embutido) e remove o criptografado
def descriptografar_arquivos_sensitiveis(caminho_entrada, chave_aes):
    if not os.path.exists(caminho_entrada):
        print(f"[⚠️] Arquivo '{caminho_entrada}' não encontrado.")
        return

    with open(caminho_entrada, "rb") as f:
        dados = f.read()

    iv = dados[:16]  # Extrai o IV do início do arquivo
    dados_criptografados = dados[16:]

    cipher = Cipher(algorithms.AES(chave_aes), modes.CBC(iv))
    decryptor = cipher.decryptor()

    dados_descriptografados = decryptor.update(dados_criptografados) + decryptor.finalize()

    # Remove padding manual
    padding_len = dados_descriptografados[-1]
    dados_descriptografados = dados_descriptografados[:-padding_len]

    caminho_saida = caminho_entrada.replace(".enc", "")
    with open(caminho_saida, "wb") as f:
        f.write(dados_descriptografados)

    print(f"[✅] Arquivo descriptografado: {caminho_saida}")

# 🔐 Criptografa os arquivos sensíveis de um votante específico
def criptografar_arquivos_sensitiveis(votante_id):
    chave_aes = carregar_chave_aes(votante_id)
    chave_aes_path = f"chaves_simetricas/chave_simetrica_{votante_id}.key"

    
    if not os.path.exists(chave_aes_path):
        print(f"[ℹ️] Chave AES não encontrada. Gerando nova chave AES para {votante_id}...")
        chave_aes = gerar_chave_aes()
        salvar_chave_aes(chave_aes, votante_id)
    else:
        chave_aes = carregar_chave_aes(votante_id)

    arquivos = [
        f"votos/votos_{votante_id}.txt"
    ]

    for arquivo in arquivos:
        if os.path.exists(arquivo):
            criptografar_arquivo(arquivo, chave_aes)
            print(f"[🔐] Arquivo '{arquivo}' criptografado com sucesso.")
