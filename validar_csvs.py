import os

PASTA_VOTOS = "votos"
COLUNAS_ESPERADAS = 5

def validar_csv(path_csv):
    with open(path_csv, "r", encoding="utf-8") as f:
        for i, linha in enumerate(f, start=1):
            partes = linha.strip().split(",")
            if len(partes) != COLUNAS_ESPERADAS:
                print(f"[ERRO] {path_csv} - Linha {i} tem {len(partes)} colunas: {linha.strip()}")

def main():
    for arquivo in os.listdir(PASTA_VOTOS):
        if arquivo.endswith(".csv"):
            caminho = os.path.join(PASTA_VOTOS, arquivo)
            validar_csv(caminho)

if __name__ == "__main__":
    main()
