from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

def criptografar_com_chave_publica(mensagem, caminho_chave_publica):
    """
    Criptografa uma mensagem usando a chave pública RSA do destinatário.

    Args:
        mensagem (str): Texto simples que será criptografado.
        caminho_chave_publica (str): Caminho para o arquivo .pem com a chave pública.

    Returns:
        bytes: Mensagem criptografada com RSA.
    """
    # Abre o arquivo da chave pública
    with open(caminho_chave_publica, "rb") as f:
        chave_publica = serialization.load_pem_public_key(f.read())

    # Codifica a mensagem para bytes
    mensagem_bytes = mensagem.encode("utf-8")

    # Criptografa a mensagem usando padding OAEP com SHA-256
    mensagem_criptografada = chave_publica.encrypt(
        mensagem_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return mensagem_criptografada

def carregar_chave_publica(caminho):
    """
    Carrega uma chave pública a partir de um arquivo .pem.

    Args:
        caminho (str): Caminho para o arquivo da chave pública.

    Returns:
        cryptography.PublicKey: Objeto de chave pública.
    """
    with open(caminho, "rb") as f:
        return serialization.load_pem_public_key(f.read())
