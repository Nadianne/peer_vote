import json
import socket
import base64
import os
import sys
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dados_candidatos import candidatos
from config import PORTA_VOTACAO
from seguranca_arquivos import criptografar_arquivos_sensitiveis
from registro_voto import RegistroVoto
import csv

HOST = '127.0.0.1'

# Códigos ANSI para estilizar com cores
class Cores:
    HEADER = '\033[95m'
    AZUL = '\033[94m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    NEGRITO = '\033[1m'
    RESET = '\033[0m'
# Exibe os candidatos disponíveis para determinado cargo
def exibir_candidatos(cargo):
    print(f"\n{Cores.HEADER}{'═' * 50}")
    print(f"{Cores.NEGRITO}🗳️  CANDIDATOS PARA {cargo.upper():^30} {Cores.HEADER}")
    print(f"{'═' * 50}{Cores.RESET}")
    print(f"{Cores.AZUL}{'Número':<8} {'Nome':<20} Partido{Cores.RESET}")
    print(f"{'-' * 50}")

    for numero, (nome, partido) in candidatos[cargo].items():
        emoji = "✅" if int(numero) % 2 == 0 else "🔹"
        print(f"{Cores.VERDE}{numero:<8}{Cores.RESET} {nome:<20} {partido} {emoji}")

    print(f"{Cores.HEADER}{'═' * 50}{Cores.RESET}")
# Função para assinar um voto usando a chave privada do votante
def assinar_voto(voto_str, votante):
    caminho_chave = f"chaves_privadas/privada_{votante}.pem"
    if not os.path.exists(caminho_chave):
        raise FileNotFoundError(f"Chave privada não encontrada para o ID '{votante}'.")

    with open(caminho_chave, "rb") as f:
        chave_privada = serialization.load_pem_private_key(f.read(), password=None)

    assinatura = chave_privada.sign(
        voto_str.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

    return base64.b64encode(assinatura).decode()
# Função para criptografar o voto antes de enviar
def criptografar_mensagem(mensagem_json, id_destino):
    chave_aes = os.urandom(32)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(chave_aes), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padding_length = 16 - (len(mensagem_json.encode()) % 16)
    mensagem_padded = mensagem_json + chr(padding_length) * padding_length
    mensagem_criptografada = encryptor.update(mensagem_padded.encode()) + encryptor.finalize()
    caminho_chave_publica = f"chaves_publicas/publica_{id_destino}.pem"
    if not os.path.exists(caminho_chave_publica):
        raise FileNotFoundError(f"Chave pública não encontrada para o ID '{id_destino}'.")
    # Carrega a chave pública do nó de destino
    with open(caminho_chave_publica, "rb") as f:
        chave_publica = serialization.load_pem_public_key(f.read())

    chave_aes_criptografada = chave_publica.encrypt(
        chave_aes,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    return {
        "chave_aes": base64.b64encode(chave_aes_criptografada).decode(),
        "iv": base64.b64encode(iv).decode(),
        "mensagem": base64.b64encode(mensagem_criptografada).decode()
    }

import time  # adicione no topo, se ainda não tiver importado
# Função para compor, assinar, criptografar e enviar um voto
def enviar_voto(votante, cargo, voto, id_destino, porta_votacao):
    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    voto_str = f"VOTE:{votante}:{cargo}:{voto}:{horario}"

    try:
        assinatura = assinar_voto(voto_str, votante)
    except Exception as e:
        print(f"{Cores.VERMELHO}[ERRO]{Cores.RESET} Ao assinar o voto: {e}")
        return

    voto_dict = {
        "votante": votante,
        "cargo": cargo,
        "nome": voto,
        "partido": candidatos[cargo][voto][1],
        "horario": horario,
        "voto_str": voto_str,
        "assinatura": assinatura
    }

    mensagem_json = json.dumps(voto_dict)

    try:
        pacote = criptografar_mensagem(mensagem_json, id_destino)
    except Exception as e:
        print(f"{Cores.VERMELHO}[ERRO]{Cores.RESET} Ao criptografar a mensagem: {e}")
        return

    # Tenta enviar até 3 vezes
    for tentativa in range(3):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
                cliente.connect((HOST, porta_votacao))
                cliente.sendall(json.dumps(pacote).encode())
                print(f"{Cores.VERDE}[✅] Voto para {cargo.upper()} enviado com sucesso.{Cores.RESET}")
                return voto_dict
        except Exception as e:
            print(f"{Cores.VERMELHO}[TENTATIVA {tentativa+1}] Erro ao enviar voto: {e}{Cores.RESET}")
            time.sleep(2)  # espera 2 segundos antes de tentar de novo

    print(f"{Cores.VERMELHO}[❌] Todas as tentativas de envio falharam.{Cores.RESET}")
    return
# Função principal que executa o processo de votação do usuário
def iniciar_cliente(votante, porta_destino):
    if not os.path.exists(f"chaves_privadas/privada_{votante}.pem"):
        print(f"{Cores.VERMELHO}[ERRO]{Cores.RESET} Chave privada não encontrada para o votante '{votante}'.")
        return

    id_destino = input("Digite o ID do nó destino para envio dos votos: ")

    print(f"\n{Cores.AMARELO}*** INICIANDO VOTAÇÃO PARA {votante.upper()} ***{Cores.RESET}")

    votos_registrados = []

    for cargo in candidatos.keys():
        exibir_candidatos(cargo)

        while True:
            voto = input(f"\nDigite o número do candidato para {cargo}: ")
            if voto in candidatos[cargo]:
                break
            print(f"{Cores.VERMELHO}Número inválido. Tente novamente.{Cores.RESET}")

        nome, partido = candidatos[cargo][voto]

        # Salva localmente com RegistroVoto
        registro = RegistroVoto(votante, cargo, nome, partido)
        registro.salvar()

        # Envia para o servidor normalmente
        voto_enviado = enviar_voto(votante, cargo, voto, id_destino, porta_destino)
        if voto_enviado:
            votos_registrados.append(voto_enviado)

    print(f"\n{Cores.AMARELO}🔐 Criptografando arquivos sensíveis...{Cores.RESET}")
    criptografar_arquivos_sensitiveis(votante)
    print(f"{Cores.VERDE}✅ Arquivos criptografados com sucesso!{Cores.RESET}")

    print(f"\n{Cores.VERDE}[✔️] Votação finalizada com sucesso!{Cores.RESET}")
# Execução via terminal
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python cliente_voto.py <id_do_votante> <porta_destino>")
        sys.exit(1)

    votante = sys.argv[1]
    porta_destino = int(sys.argv[2])

    with open("id_votante.txt", "w") as f:
        f.write(votante)

    iniciar_cliente(votante, porta_destino)  