import os
import json

def padronizar_campos_em_votos(pasta="votos"):
    # Percorre todos os arquivos na pasta de votos
    for nome_arquivo in os.listdir(pasta):
        caminho = os.path.join(pasta, nome_arquivo)
        
        # Filtra apenas arquivos JSON
        if nome_arquivo.endswith(".json"):
            with open(caminho, "r", encoding="utf-8") as f:
                try:
                    dados = json.load(f)  # Lê o conteúdo do JSON
                except Exception as e:
                    print(f"[ERRO] Não foi possível ler {nome_arquivo}: {e}")
                    continue  # Pula arquivos com erro

            votos_corrigidos = []

            # Para cada voto, padroniza os campos com letras minúsculas
            for voto in dados:
                voto_corrigido = {
                    "votante": voto.get("votante") or voto.get("Votante"),
                    "cargo": voto.get("cargo") or voto.get("Cargo"),
                    "nome": voto.get("nome") or voto.get("Nome"),
                    "partido": voto.get("partido") or voto.get("Partido"),
                    "horario": voto.get("horario") or voto.get("Horario"),
                    "hash": voto.get("hash") or voto.get("Hash"),
                }
                votos_corrigidos.append(voto_corrigido)

            # Sobrescreve o arquivo com os campos corrigidos
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(votos_corrigidos, f, indent=4, ensure_ascii=False)

            print(f"[✓] Arquivo corrigido: {nome_arquivo}")

# Executa a padronização ao rodar o script
padronizar_campos_em_votos()
