import os
import csv

PASTA_ORIGINAL = "votos"
PASTA_CORRIGIDA = "votos_corrigidos"
COLUNAS_ESPERADAS = 5

os.makedirs(PASTA_CORRIGIDA, exist_ok=True)

def corrigir_linha(linha):
    partes = linha.strip().split(",")
    if len(partes) == COLUNAS_ESPERADAS:
        return partes
    else:
        # Junta tudo antes do horário como uma única string com vírgulas (candidato ou partido com vírgula no nome)
        cargo = partes[0]
        nome = partes[1]
        # junta o meio até o penúltimo item (horário)
        partido = ",".join(partes[2:-2]).strip()
        horario = partes[-2].strip()
        hash_voto = partes[-1].strip()
        return [cargo, nome, f'"{partido}"', horario, hash_voto]

def corrigir_csv(caminho_origem, caminho_destino):
    with open(caminho_origem, "r", encoding="utf-8") as fin, \
         open(caminho_destino, "w", newline="", encoding="utf-8") as fout:
        
        leitor = csv.reader(fin)
        escritor = csv.writer(fout)

        for linha in leitor:
            if len(linha) == COLUNAS_ESPERADAS:
                escritor.writerow(linha)
            else:
                nova_linha = corrigir_linha(",".join(linha))
                escritor.writerow(nova_linha)

def main():
    for arquivo in os.listdir(PASTA_ORIGINAL):
        if arquivo.endswith(".csv"):
            origem = os.path.join(PASTA_ORIGINAL, arquivo)
            destino = os.path.join(PASTA_CORRIGIDA, arquivo)
            corrigir_csv(origem, destino)
            print(f"[OK] Corrigido: {arquivo}")

if __name__ == "__main__":
    main()
