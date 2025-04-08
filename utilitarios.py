# utilitarios.py
import os
import csv

def salvar_csv_seguro(votante, cargo, nome, partido, horario_str, hash_voto):
    arquivo_voto_csv = os.path.join("votos", f"votos_{votante}.csv")
    header = ["Cargo", "Nome", "Partido", "Horario", "Hash"]

    existe = os.path.exists(arquivo_voto_csv)
    with open(arquivo_voto_csv, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not existe or os.path.getsize(arquivo_voto_csv) == 0:
            writer.writerow(header)
        writer.writerow([cargo, nome, partido, horario_str, hash_voto])
