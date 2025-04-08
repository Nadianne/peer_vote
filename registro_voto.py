import os
import hashlib
from datetime import datetime
from utilitarios import salvar_csv_seguro  # Função externa que salva voto em CSV seguro

class RegistroVoto:
    """
    Classe responsável por representar e registrar um voto individual,
    garantindo integridade com hash e salvando em arquivos de forma estruturada.
    """

    def __init__(self, votante, cargo, nome, partido, horario=None):
        """
        Inicializa um novo objeto de voto.
        
        Args:
            votante (str): Identificador único do votante (ex: 'usuario1').
            cargo (str): Cargo ao qual o voto se refere (ex: 'Presidente').
            nome (str): Nome do candidato votado.
            partido (str): Partido do candidato.
            horario (datetime, opcional): Momento do voto. Se não for passado, usa o horário atual.
        """
        self.votante = votante
        self.cargo = cargo
        self.nome = nome
        self.partido = partido
        self.horario = horario if horario else datetime.now()

    def gerar_hash(self):
        """
        Gera um hash SHA-256 com base nos dados do voto.
        
        Returns:
            str: Hash do voto, garantindo sua integridade.
        """
        dados = f"{self.votante}:{self.cargo}:{self.nome}:{self.partido}:{self.horario}"
        return hashlib.sha256(dados.encode()).hexdigest()

    def salvar(self):
        """
        Salva o voto em dois formatos:
        - `.txt` com visualização humanizada do voto.
        - `.csv` estruturado e seguro (usando `salvar_csv_seguro`).
        
        Também gera um hash do voto e retorna.
        
        Returns:
            str: Hash do voto registrado.
        """
        # Formata o horário do voto como string
        horario_str = (
            self.horario.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(self.horario, datetime)
            else str(self.horario)
        )
        hash_voto = self.gerar_hash()

        # Cria a pasta 'votos' se ela não existir
        pasta = "votos"
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        # Cria visualização do voto para arquivo .txt
        voto_formatado = (
            f"{'═' * 60}\n"
            f"🗳️  VOTO REGISTRADO\n"
            f"{'═' * 60}\n"
            f"👤 Votante: {self.votante}\n"
            f"🏛️ Cargo: {self.cargo}\n"
            f"👔 Candidato: {self.nome}\n"
            f"🎯 Partido: {self.partido}\n"
            f"🕒 Horário: {horario_str}\n"
            f"🔐 Hash: {hash_voto}\n"
            f"{'═' * 60}\n\n"
        )

        # Salva o voto visualmente no arquivo .txt do votante
        arquivo_voto_txt = os.path.join(pasta, f"votos_{self.votante}.txt")
        with open(arquivo_voto_txt, "a", encoding="utf-8") as f:
            f.write(voto_formatado)

        # Salva também em CSV seguro
        salvar_csv_seguro(self.votante, self.cargo, self.nome, self.partido, horario_str, hash_voto)
        
        print(f"[✅] Voto salvo como {arquivo_voto_txt} com sucesso.")
        return hash_voto
