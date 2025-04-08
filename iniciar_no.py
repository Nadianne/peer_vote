import sys
from main import start_servidor, registrar_no_peers  # Importa funções principais do nó
from config import HOST  # Endereço IP do host (normalmente localhost)

if __name__ == "__main__":
    print("\n📡 Iniciando um novo nó PeerVote...\n")

    # Solicita o ID do nó ao usuário
    ID_NO_ATUAL = input("🆔 Digite o ID do nó (ex: usuario1): ").strip()

    # Solicita a porta em que este nó deve escutar conexões
    porta_str = input("🔌 Digite a porta para este nó (ex: 5050): ").strip()

    # Valida entradas do usuário
    if not ID_NO_ATUAL or not porta_str.isdigit():
        print("\n❌ Entrada inválida. Encerrando.")
        sys.exit(1)

    PORTA_VOTACAO = int(porta_str)
    
    # Exibe confirmação de inicialização
    print(f"\n✅ Inicializando nó '{ID_NO_ATUAL}' na porta {PORTA_VOTACAO}...\n")

    # Registra o nó atual no arquivo de peers (para comunicação P2P)
    registrar_no_peers(HOST, PORTA_VOTACAO)

    # Inicia o servidor de votação deste nó
    start_servidor(ID_NO_ATUAL, PORTA_VOTACAO)
