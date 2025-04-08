# Peer_vote
 Projeto da disciplina de Sistemas distribuídos. 
 
 Sistema de votação P2P com segurança avançada: criptografia híbrida (RSA + AES), assinatura digital, sincronização de horário e distribuição de resultados entre nós. 

 # 🗳️ PeerVote — Sistema de Votação P2P com Criptografia e Segurança

**PeerVote** é um sistema de votação descentralizado baseado em arquitetura P2P, com ênfase em **segurança, integridade e privacidade** dos votos. Os nós trocam informações via sockets TCP e UDP, usando criptografia híbrida (RSA + AES), assinaturas digitais e sincronização de horário.

---

## 📌 Funcionalidades

✅ Arquitetura peer-to-peer (P2P) com descoberta automática de nós  
✅ Votação segura com criptografia híbrida (RSA + AES)  
✅ Assinatura digital dos votos (RSA + PSS)  
✅ Armazenamento distribuído e estruturado dos votos  
✅ Sincronização de horário entre os nós (UDP)  
✅ Contagem automática e validação dos votos  

---

## 🧠 Tecnologias e Conceitos

- **Python 3**
- **Sockets TCP/UDP**
- **Criptografia RSA & AES**
- **Assinatura Digital com PSS**
- **Codificação Base64**
- **Hash SHA-256**
- **Arquivos CSV, JSON e TXT**
- **Arquitetura descentralizada**
- **Sincronização de tempo via UDP**

---

## ⚙️ Pré-requisitos

- Python 3.8+
- Bibliotecas: `cryptography`, `tabulate`, `panda`

  # 🗳️ Passo a Passo

  ## 🧾 Passo 1 – Gerar Chaves
[images/01.png]
```bash
python gerar_chaves.py
python gerar_chaves_simetricas.py

