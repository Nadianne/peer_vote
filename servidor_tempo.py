# servidor_tempo.py

import socket  # Biblioteca para comunicação via sockets
from datetime import datetime  # Para obter o horário atual

# Define o host e a porta do servidor de tempo
HOST = '127.0.0.1'
PORT = 6000  # Porta usada também pelo cliente, deve ser mantida igual

def servidor_tempo():
    # Cria um socket TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permite reutilizar a porta se estiver em estado TIME_WAIT
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Associa o socket ao host e porta definidos
        s.bind((HOST, PORT))
        # Coloca o socket em modo de escuta, pronto para aceitar conexões
        s.listen()
        print(f"[🕒] Servidor de tempo rodando em {HOST}:{PORT}...")

        # Loop principal que aguarda conexões de clientes
        while True:
            conn, addr = s.accept()  # Aceita uma nova conexão
            with conn:
                print(f"[⏰] Conexão de {addr}")
                # Obtém o horário UTC atual e formata como string
                agora = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                # Envia o horário ao cliente conectado
                conn.sendall(agora.encode())

# Executa o servidor se este arquivo for chamado diretamente
if __name__ == "__main__":
    servidor_tempo()
