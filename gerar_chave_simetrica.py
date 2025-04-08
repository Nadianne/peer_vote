import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

def carregar_chave_publica(votante_id):
    caminho = f"chaves_publicas/publica_{votante_id}.pem"
    with open(caminho, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def gerar_chave_simetrica_criptografada(votante_id):
    chave_aes = os.urandom(32)  # 256 bits
    chave_publica = carregar_chave_publica(votante_id)

    chave_criptografada = chave_publica.encrypt(
        chave_aes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Salvar chave criptografada
    caminho_saida = f"chaves_simetricas/chave_simetrica_{votante_id}.key"
    with open(caminho_saida, "wb") as f:
        f.write(chave_criptografada)

    print(f"✅ Chave AES criptografada com RSA e salva em {caminho_saida}")

if __name__ == "__main__":
    votante_id = input("Digite o ID do votante (ex: usuario1): ")
    gerar_chave_simetrica_criptografada(votante_id)
