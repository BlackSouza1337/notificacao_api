# 📲 Notificação API via BLiP + Oracle

Este projeto implementa uma API em Flask que realiza o envio automatizado de mensagens de WhatsApp via **BLiP API**, utilizando dados extraídos de um banco **Oracle**. O disparo das notificações é feito de forma programada por um job agendador.

---

## 📁 Estrutura do Projeto

```
notificacao_api/
│
├── app.py                   # API principal com Flask para envio de notificações via BLiP
├── notificacao_job.py       # Script agendador que dispara notificações periodicamente
├── requirements.txt         # Dependências Python necessárias para o projeto
├── .env                     # Variáveis de ambiente (credenciais e configurações sensíveis)
├── .gitignore               # Ignora arquivos não rastreados pelo Git
├── logs/                    # Diretório para armazenamento dos logs
│   └── notificacao.log      # Log estruturado (JSON) com execuções e erros
├── README.md                # Esta documentação
└── start.bat                # Script para iniciar app.py e notificacao_job.py em janelas separadas
```

---

## ⚙️ Requisitos

- Python 3.8 ou superior
- Acesso à internet para chamadas à API BLiP
- Acesso à base de dados Oracle
- Permissões de envio via WhatsApp BLiP (templates aprovados)

---

## 📦 Instalação

1. Clone o repositório:

```bash
git clone https://github.com/BlackSouza1337/notificacao_api
cd notificacao_api
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` com os dados do Oracle e da API BLiP:

```dotenv
# Oracle
DB_USER=usuario
DB_PASSWORD=senha
DB_DSN_HOST=host_oracle
DB_DSN_PORT=1521
DB_DSN_SERVICE=nome_servico

# BLiP
URLBLIP_COMMANDS=https://http.msging.net/commands
URLBLIP_MESSAGES=https://http.msging.net/messages
KEYBLIP=Token_do_BLIP
TEMPLATE_NAME=TEMPLATE_NAME
NAMESPACE=NAMESPACE
```

---

## 🚀 Execução

### Iniciar a API e o Job automaticamente:

```bat
start.bat
```

Este script:

1. Inicia o `app.py` (API Flask)
2. Aguarda 20 segundos
3. Inicia o `notificacao_job.py` (agendador de envio a cada 5 minutos)

---

## 🔄 Funcionamento

### app.py

- Rota POST `/send_notification` que:
  - Executa SELECT no banco Oracle
  - Formata e valida números de telefone
  - Consulta o identificador WhatsApp via BLiP
  - Dispara o template via BLiP API
  - Atualiza o status da notificação no banco

### notificacao_job.py

- Verifica se a API Flask está disponível
- Executa `POST /send_notification` a cada 5 minutos
- Logs estruturados em JSON no diretório `logs/`

---

## 📊 Logs

Os logs são registrados em `logs/notificacao.log` no formato JSON:

```json
{
  "timestamp": "2025-05-15T10:40:00",
  "level": "INFO",
  "message": "Notificações processadas com sucesso.",
  "data": {
    "sent": 8,
    "failed": 2
  }
}
```

---

## 🧪 Testes

### Testar envio manual:

```bash
curl -X POST http://localhost:5000/send_notification
```

---

## 🛠️ Tecnologias utilizadas

- Python 3
- Flask
- cx_Oracle
- schedule
- BLiP API (Take.net)
- Oracle Database

---

## 👤 Autor

**Rafael Souza**  
Analista de Sistemas | Analista de Suporte  

📧 rafaelsouzacmp@gmail.com  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-perfil-blue?logo=linkedin)](https://www.linkedin.com/in/rafael-souza-ti/)

---

🔗 Parte do banco de dados para coleta e preparação dos dados
Este repositório contém os scripts Oracle SQL que suportam a API de notificações.

https://github.com/jaovleal/API_BLIP_PAS_Scripts_SQL

🛠️ João Leal – Desenvolvedor responsável pela criação da tabela principal, procedures e triggers que alimentam a API.

---

## 📝 Licença

MIT License

Copyright (c) 2025 BlackSouza1337

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.