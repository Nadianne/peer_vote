import socket
from datetime import datetime

class ClienteTempo:
    """Cliente que solicita a sincronização do horário ao servidor de tempo."""

    def __init__(self, servidor_tempo="127.0.0.1", porta=6000):
        # Define o endereço IP e porta do servidor de tempo
        self.servidor_tempo = servidor_tempo
        self.porta = porta

    def sincronizar_relogio(self):
        """
        Obtém o horário UTC do servidor e o retorna como objeto datetime.
        Utiliza conexão via socket TCP.
        """
        try:
            # Cria o socket TCP
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Conecta ao servidor de tempo
            cliente.connect((self.servidor_tempo, self.porta))
            
            # Recebe o horário enviado pelo servidor
            horario_servidor = cliente.recv(1024).decode()
            cliente.close()

            print(f"[SINCRONIZAÇÃO] Horário recebido: {horario_servidor}")

            # Mostra o horário local para comparação
            horario_local = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[LOCAL] Horário atual: {horario_local}")

            # Converte o horário do servidor para um objeto datetime e retorna
            return datetime.strptime(horario_servidor, "%Y-%m-%d %H:%M:%S")

        except Exception as erro:
            # Em caso de erro, exibe a mensagem e retorna None
            print(f"[ERRO] Falha na sincronização: {erro}")
            return None  # importante para que o main.py possa tratar corretamente
