# Importa bibliotecas necessárias para threads, sockets, manipulação de arquivos, criptografia e outras funcionalidades
import threading
import socket
import time
from collections import Counter
from datetime import datetime
import pandas as pd
import json
from tabulate import tabulate
from collections import defaultdict
import os
import sys
from seguranca_arquivos import criptografar_arquivos_sensitiveis, criptografar_arquivo
from seguranca_arquivos import descriptografar_arquivos_sensitiveis
from registro_voto import RegistroVoto
from dados_candidatos import candidatos
from cliente_tempo import ClienteTempo
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import InvalidSignature
import base64
from config import HOST, PORTA_VOTACAO, PORTA_RESULTADO, PORTA_TEMPO
from compartilhar_resultados import servidor as servidor_resultado, enviar_resultado_para_no
from contar_votos import contar_votos

# Define o horário de início da votação
inicio_votacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Garante que o diretório "votos" exista
if not os.path.exists("votos"):
    os.makedirs("votos")

# Função para carregar os peers registrados no arquivo peers.json
def carregar_peers():
    try:
        with open("peers.json", "r") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return []
            return json.loads(conteudo)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar peers.json: {e}")
        return []

# Função para verificar a assinatura de um voto
def verificar_assinatura(voto_str, assinatura_base64, votante):
    caminho_chave_publica = f"chaves_publicas/publica_{votante}.pem"
    if not os.path.exists(caminho_chave_publica):
        print(f"[ERRO] Chave pública não encontrada para o votante '{votante}'")
        return False
    try:        
        # Carrega a chave pública do votante
        with open(caminho_chave_publica, "rb") as f:
            chave_publica = serialization.load_pem_public_key(f.read())
        assinatura = base64.b64decode(assinatura_base64)
        chave_publica.verify(
            assinatura,
            voto_str.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True 
    except Exception as e:
        print(f"[⚠️] Erro ao verificar assinatura do votante '{votante}': {e}")
        return False
def handle_client(conexao, endereco, ID_NO_ATUAL):
    print(f"[NOVA CONEXÃO] Conectado por {endereco}")
    try:
        # Recebe os dados enviados pelo cliente
        dados_recebidos = conexao.recv(4096)

        # Verifica se a mensagem é um pedido de resultados
        try:
            dados_decodificados = dados_recebidos.decode()
            if dados_decodificados.strip() == "RESULTADOS?":
                resultado_dict = contar_votos(retornar_dict=True)
                if resultado_dict:
                    resposta = json.dumps(resultado_dict, indent=4, ensure_ascii=False)
                    conexao.sendall(resposta.encode())
                else:
                    conexao.sendall("[⚠️] Nenhum resultado disponível.".encode())
                return
            else:
                pacote = json.loads(dados_decodificados)
        except (UnicodeDecodeError, json.JSONDecodeError):
            print("[ERRO] Dados recebidos não são JSON nem comando válido.")
            conexao.sendall("[ERRO] Formato de mensagem inválido.".encode())
            return

        # Mensagens de voto devem conter "chave_aes", "iv" e "mensagem"
        if all(k in pacote for k in ("chave_aes", "iv", "mensagem")):
            # Descriptografando o pacote
            chave_aes_criptografada = base64.b64decode(pacote["chave_aes"])
            iv = base64.b64decode(pacote["iv"])
            mensagem_criptografada = base64.b64decode(pacote["mensagem"])

            # Carrega chave privada do nó atual
            caminho_chave_privada = f"chaves_privadas/privada_{ID_NO_ATUAL}.pem"
            with open(caminho_chave_privada, "rb") as f:
                chave_privada = serialization.load_pem_private_key(f.read(), password=None)

            # Descriptografa a chave AES
            chave_aes = chave_privada.decrypt(
                chave_aes_criptografada,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Descriptografa a mensagem
            cipher = Cipher(algorithms.AES(chave_aes), modes.CBC(iv))
            decryptor = cipher.decryptor()
            mensagem_padded = decryptor.update(mensagem_criptografada) + decryptor.finalize()
            padding_length = mensagem_padded[-1]
            mensagem = mensagem_padded[:-padding_length].decode()

            # Processa os dados do voto
            voto_dict = json.loads(mensagem)
            if isinstance(voto_dict, str):
                voto_dict = json.loads(voto_dict)
            voto_dict = {k.lower(): v for k, v in voto_dict.items()}

            campos_obrigatorios = ["votante", "cargo", "nome", "partido", "horario", "assinatura"]
            for campo in campos_obrigatorios:
                if voto_dict.get(campo) is None:
                    print(f"[ERRO] Campo obrigatório '{campo}' ausente na mensagem!")
                    return

            print(f"[🗳️] {voto_dict['votante']} votou para {voto_dict['cargo']}: {voto_dict['nome']} ({voto_dict['partido']}) às {voto_dict['horario']}")

            votante = voto_dict["votante"]
            cargo = voto_dict["cargo"]
            nome = voto_dict["nome"]
            partido = voto_dict["partido"]
            horario = voto_dict["horario"]
            assinatura = voto_dict["assinatura"]

            caminho_arquivo_voto = f"votos/votos_{votante}.txt"
            votos_anteriores = []

            if os.path.exists(caminho_arquivo_voto):
                with open(caminho_arquivo_voto, "r", encoding="utf-8") as f:
                    votos_anteriores = f.readlines()
                for voto in votos_anteriores:
                    try:
                        voto_dict_linha = json.loads(voto.strip())
                        if voto_dict_linha.get("cargo") == cargo:
                            print(f"[⚠️] {votante} já votou para {cargo}. Ignorando novo voto.")
                            return
                    except Exception:
                        continue

            voto_str = f"VOTE:{votante}:{cargo}:{nome}:{horario}"

            if verificar_assinatura(voto_str, assinatura, votante):
                novo_voto = RegistroVoto(votante, cargo, nome, partido, horario)
                hash_voto = novo_voto.salvar()
                print(f"[VOTO REGISTRADO ✅] {cargo}: {nome} ({partido}) - Hash: {hash_voto}")

        
            # Tentativa de salvar resultado recebido
            try:
                if isinstance(pacote, dict) and "resultados" in pacote:
                    os.makedirs("resultados", exist_ok=True)
                    nome_arquivo = f"resultados/resultado_recebido_de_{endereco[0]}_{endereco[1]}.json"
                    with open(nome_arquivo, "w", encoding="utf-8") as f:
                        json.dump(pacote, f, indent=4, ensure_ascii=False)
                    print(f"[📥] Resultados recebidos salvos em {nome_arquivo}")
               
            except Exception as e:
                print(f"[ERRO] Não foi possível salvar os resultados recebidos: {e}")

    except Exception as erro:
        print(f"[ERRO] Falha ao processar mensagem: {type(erro).__name__} -> {erro}")
    finally:
        conexao.close()

# Função para registrar o nó no arquivo peers.json
def registrar_no_peers(ip, porta):
    novo_peer = f"{ip}:{porta}"
    peers = []

    if os.path.exists("peers.json"):
        with open("peers.json", "r") as f:
            try:
                peers = json.load(f)
            except json.JSONDecodeError:
                peers = []

    if novo_peer not in peers:
        peers.append(novo_peer)
        with open("peers.json", "w") as f:
            json.dump(peers, f, indent=2)
        print(f"[✔] Nó {novo_peer} registrado no peers.json.")
    else:
        print(f"[ℹ️] Nó {novo_peer} já está registrado.")

# Função principal para iniciar o servidor
def start_servidor(ID_NO_ATUAL, PORTA_VOTACAO):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    caminho_chave_privada = f"chaves_privadas/privada_{ID_NO_ATUAL}.pem"
    if not os.path.exists(caminho_chave_privada):
        print(f"[ERRO] Chave privada não encontrada para o nó {ID_NO_ATUAL}.")
        sys.exit(1)

    horario_anterior = datetime.utcnow()
    cliente_tempo = ClienteTempo("127.0.0.1")
    horario_utc = cliente_tempo.sincronizar_relogio()

    if horario_utc:
        print(f"[⏰] Horário sincronizado com o servidor: {horario_anterior.strftime('%Y-%m-%d %H:%M:%S')} -> {horario_utc.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("[⚠️] Falha ao sincronizar o horário com o servidor. Usando horário local.")
        horario_utc = horario_anterior

    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORTA_VOTACAO))
    servidor.listen()
    print(f"[SERVIDOR] Rodando em {HOST}:{PORTA_VOTACAO}")

    inicio_votacao_path = "inicio_votacao_global.txt"
    inicio_utc_str = ""

    if os.path.exists(inicio_votacao_path):
        for tentativa in range(3):
            with open(inicio_votacao_path, "r") as f:
                inicio_utc_str = f.read().strip()
            if inicio_utc_str:
                break
            else:
                print(f"[⏳] Tentativa {tentativa+1}/3: aguardando preenchimento de '{inicio_votacao_path}'...")
                time.sleep(1)

    if inicio_utc_str:
        inicio_utc = datetime.strptime(inicio_utc_str, "%Y-%m-%d %H:%M:%S")
        print(f"[⏰] Votação iniciada globalmente em: {inicio_utc_str}")
    else:
        inicio_utc = datetime.utcnow()
        with open(inicio_votacao_path, "w") as f:
            inicio_str = inicio_utc.strftime("%Y-%m-%d %H:%M:%S")
            f.write(inicio_str)
        print(f"[🟢] Este nó iniciou a votação global em: {inicio_str}")

    tempo_encerramento = inicio_utc.timestamp() + 120
    servidor.settimeout(1)

    while True:
        tempo_atual = datetime.utcnow().timestamp()
        if tempo_atual >= tempo_encerramento:
            print("[⏲️] Tempo de votação encerrado. Contando votos...")

            contar_votos()
            peers = carregar_peers()
            for peer in peers:
                try:
                    ip, porta = peer.split(":")
                    enviar_resultado_para_no(ip, int(porta))
                except Exception as e:
                    print(f"[ERRO] Falha ao enviar resultado para {peer}: {e}")
            aguardar_resultados_apos_votacao(servidor, ID_NO_ATUAL)
            try:
                with open("id_votante.txt") as f:
                    votante_id = f.read().strip()
                print("[🔒] Iniciando criptografia automática dos arquivos sensíveis...")
                criptografar_arquivos_sensitiveis(votante_id)
            except Exception as e:
                print(f"[ERRO] Falha ao criptografar arquivos sensíveis: {e}")
            break

        try:
            conexao, endereco = servidor.accept()
            thread_cliente = threading.Thread(target=handle_client, args=(conexao, endereco, ID_NO_ATUAL))
            thread_cliente.start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[ERRO] Erro ao aceitar conexão: {e}")


def encerrar_votacao():
    print("[⏲️] Tempo de votação encerrado. Contando votos...")
    contar_votos()
    peers = carregar_peers()
    for peer in peers:
        try:
            ip, porta = peer.split(":")
            enviar_resultado_para_no(ip, int(porta))
        except Exception as e:
            print(f"[ERRO] Falha ao enviar resultado para {peer}: {e}")

    try:
        with open("id_votante.txt") as f:
            votante_id = f.read().strip()
        print("[🔒] Iniciando criptografia automática dos arquivos sensíveis...")
        criptografar_arquivos_sensitiveis(votante_id)
    except Exception as e:
        print(f"[ERRO] Falha ao criptografar arquivos sensíveis: {e}")
        
def aguardar_resultados_apos_votacao(servidor,  ID_NO_ATUAL, duracao=30):
    fim = datetime.utcnow().timestamp() + duracao
    print(f"[⏳] Aguardando resultados de outros nós por {duracao} segundos...")
    while datetime.utcnow().timestamp() < fim:
        try:
            servidor.settimeout(2)
            conexao, endereco = servidor.accept()
            thread_cliente = threading.Thread(target=handle_client, args=(conexao, endereco, ID_NO_ATUAL))
            thread_cliente.start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[ERRO] Erro ao receber resultado de outro nó: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python main.py <ID_NO_ATUAL> <PORTA_VOTACAO> <PORTA_RESULTADO>")
        sys.exit(1)

    ID_NO_ATUAL = sys.argv[1]
    try:
        PORTA_VOTACAO = int(sys.argv[2])
        PORTA_RESULTADO = int(sys.argv[3])
    except ValueError:
        print("[ERRO] As portas devem ser números inteiros.")
        sys.exit(1)

    registrar_no_peers(HOST, PORTA_VOTACAO)

    # Inicia o servidor de compartilhamento de resultados em paralelo
    threading.Thread(target=servidor_resultado, args=(PORTA_RESULTADO,), daemon=True).start()

    # Inicia o servidor de votação principal
    start_servidor(ID_NO_ATUAL, PORTA_VOTACAO)