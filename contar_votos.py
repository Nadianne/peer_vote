import os  
import pandas as pd  
import json  
from tabulate import tabulate  
from datetime import datetime, timedelta 

# Caminho da pasta onde os votos estão armazenados
PASTA_VOTOS = 'votos/'

# Arquivo que contém o horário de início da votação
ARQUIVO_INICIO = 'inicio_votacao_global.txt'

# Dicionário com emojis representando os cargos
EMOJIS_CARGOS = {
    "Presidente": "👑",
    "Governador": "🏛️",
    "Senador": "🎓",
    "Deputado Federal": "📘",
    "Deputado Estadual": "📗"
}

# Função principal que realiza a contagem de votos
def contar_votos(exibir_resultado=True, salvar_arquivo=True) -> dict:
    # Tenta ler o horário de início da votação a partir do arquivo
    try:
        with open(ARQUIVO_INICIO, "r") as f:
            inicio_str = f.read().strip()
            inicio_votacao = datetime.strptime(inicio_str, "%Y-%m-%d %H:%M:%S")
            fim_votacao = inicio_votacao + timedelta(minutes=2)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{ARQUIVO_INICIO}' não encontrado.")
        return {}
    except Exception as e:
        print(f"[ERRO] Erro ao ler horário de início: {e}")
        return {}

    # Lê todos os arquivos CSV da pasta de votos e armazena em uma lista
    dados = []
    for arquivo in os.listdir(PASTA_VOTOS):
        if arquivo.endswith(".csv"):
            df = pd.read_csv(os.path.join(PASTA_VOTOS, arquivo))
            dados.append(df)

    # Se não houver dados, emite aviso e retorna
    if not dados:
        print("[⚠️] Nenhum voto encontrado.")
        return {}

    # Junta todos os DataFrames em um só
    df_total = pd.concat(dados, ignore_index=True)

    # Agrupa por cargo, nome e partido, e conta os votos
    resultado = df_total.groupby(["Cargo", "Nome", "Partido"]).size().reset_index(name="Total de Votos")

    # Remove candidatos inválidos (com nome numérico ou vazio)
    resultado = resultado[resultado["Nome"].apply(lambda x: isinstance(x, str) and not x.isnumeric())]

    # Se ativado, exibe o resultado no terminal
    if exibir_resultado:
        print("\n" + "=" * 65)
        print("🎉 RESULTADO DAS ELEIÇÕES POR CARGO")
        print("=" * 65)
        print(f"🕒 Início da votação: {inicio_votacao.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏲️  Fim da votação:    {fim_votacao.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 65 + "\n")

        # Exibe o resultado separado por cargo com emojis e tabela formatada
        for cargo in resultado["Cargo"].unique():
            emoji = EMOJIS_CARGOS.get(cargo, "🗳️")
            print(f"{emoji} {cargo}")
            tabela = resultado[resultado["Cargo"] == cargo][["Nome", "Partido", "Total de Votos"]]
            print(tabulate(tabela, headers="keys", tablefmt="fancy_grid", showindex=False))
            print()

    # Prepara dicionário final com os dados formatados
    resultado_final = {
        "InicioVotacao": inicio_votacao.strftime("%Y-%m-%d %H:%M:%S"),
        "FimVotacao": fim_votacao.strftime("%Y-%m-%d %H:%M:%S"),
        "Resultados": {}
    }

    # Estrutura os dados por cargo
    for cargo in resultado["Cargo"].unique():
        resultado_final["Resultados"][cargo] = []
        cargo_df = resultado[resultado["Cargo"] == cargo]
        for _, row in cargo_df.iterrows():
            resultado_final["Resultados"][cargo].append({
                "Nome": row["Nome"],
                "Partido": row["Partido"],
                "Total de Votos": int(row["Total de Votos"])
            })

    # Salva o resultado em um arquivo JSON, se solicitado
    if salvar_arquivo:
        with open("resultado_votacao.json", "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=4, ensure_ascii=False)
        print("✅ Resultado salvo em 'resultado_votacao.json'")

    return resultado_final

# Permite executar diretamente via terminal
if __name__ == "__main__":
    contar_votos()
