import os
import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def gerar_chaves(votante_id):
    # Cria diretórios para armazenar as chaves, se ainda não existirem
    os.makedirs("chaves_privadas", exist_ok=True)
    os.makedirs("chaves_publicas", exist_ok=True)

    # Gera uma nova chave privada RSA (2048 bits)
    chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Serializa e salva a chave privada no formato PEM (sem senha)
    caminho_privada = f"chaves_privadas/privada_{votante_id}.pem"
    with open(caminho_privada, "wb") as f:
        f.write(chave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Gera a chave pública correspondente à chave privada
    chave_publica = chave_privada.public_key()
    caminho_publica = f"chaves_publicas/publica_{votante_id}.pem"

    # Serializa e salva a chave pública no formato PEM
    with open(caminho_publica, "wb") as f:
        f.write(chave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Mensagem de sucesso para o usuário
    print(f"✔️ Chaves RSA geradas para o votante {votante_id}!")
    print(f"🔒 Privada: {caminho_privada}")
    print(f"🔓 Pública: {caminho_publica}")

if __name__ == "__main__":
    # Verifica se o ID do votante foi passado como argumento
    if len(sys.argv) < 2:
        print("❌ Uso: python gerar_chaves.py <ID_do_votante>")
        sys.exit(1)

    # Executa a geração das chaves com o ID fornecido
    id_votante = sys.argv[1]
    gerar_chaves(id_votante)
