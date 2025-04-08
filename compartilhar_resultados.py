import socket  
import json    
import threading  

# Função para iniciar um servidor TCP que escuta na porta especificada
def servidor(porta_resultado):
    try:
        # Cria o socket TCP/IP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Permite reuso da porta mesmo após encerramento abrupto
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Associa o socket a todas as interfaces disponíveis e à porta especificada
            s.bind(('0.0.0.0', porta_resultado))
            # Inicia o socket em modo de escuta por conexões
            s.listen()
            print(f"[🟢] Aguardando resultados de outros nós na porta {porta_resultado}...")

            # Loop infinito para aceitar múltiplas conexões
            while True:
                conn, addr = s.accept()  # Aceita nova conexão
                # Cria e inicia uma thread separada para lidar com cada conexão
                thread = threading.Thread(target=lidar_com_requisicao, args=(conn, addr), daemon=True)
                thread.start()
    except OSError as e:
        # Em caso de erro na porta (ex: já em uso), exibe uma mensagem
        print(f"[⚠️] Erro ao iniciar servidor de resultados na porta {porta_resultado}: {e}")

# Função chamada para processar dados recebidos de uma conexão
def lidar_com_requisicao(conn, addr):
    with conn:
        print(f"[📥] Conectado por {addr}")
        # Recebe até 65536 bytes da mensagem e decodifica para string
        dados = conn.recv(65536).decode()
        print(f"[DEBUG] Dados recebidos de {addr}:")
        print(dados)

        try:
            # Tenta decodificar os dados como JSON
            resultado = json.loads(dados)
            # Gera nome de arquivo com base no IP e porta de origem
            nome_arquivo = f"resultado_recebido_{addr[0]}_{addr[1]}.json"
            # Salva o resultado em um arquivo local
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(resultado, f, indent=4, ensure_ascii=False)
            print(f"[✔️] Resultado salvo em {nome_arquivo}")
        except json.JSONDecodeError as e:
            # Caso o conteúdo recebido não seja um JSON válido
            print(f"[ERRO] Resultado recebido não é um JSON válido: {e}")

# Função para enviar um arquivo JSON de resultado para outro nó via socket TCP
def enviar_resultado_para_no(ip_destino, porta=5050, caminho_arquivo="resultado_votacao.json"):
    """Envia o resultado da votação para outro nó na rede."""
    try:
        # Abre o arquivo local contendo o resultado da votação
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            resultado = f.read()

        # Cria socket cliente e conecta ao IP e porta do nó de destino
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_destino, porta))
            # Envia os dados lidos do arquivo
            s.sendall(resultado.encode())
            print(f"[📤] Resultado enviado para {ip_destino}:{porta}")

    except Exception as e:
        # Captura e exibe erros genéricos de conexão ou leitura de arquivo
        print(f"[ERRO] Falha ao enviar resultado para {ip_destino}:{porta}: {e}")