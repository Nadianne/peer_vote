from compartilhar_resultados import receber_resultado

# Inicia o processo de recepção dos resultados de outros nós
receber_resultado()

# Mantém o script ativo indefinidamente para continuar recebendo conexões
import time
while True:
    time.sleep(1)
