import os
import json
import uuid
import cx_Oracle
import logging
from flask import Flask, jsonify, request
from urllib import request as urllib_request
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/notificacao.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Dados Oracle
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN_HOST = os.getenv("DB_DSN_HOST")
DB_DSN_PORT = os.getenv("DB_DSN_PORT")
DB_DSN_SERVICE = os.getenv("DB_DSN_SERVICE")

DB_DSN = cx_Oracle.makedsn(DB_DSN_HOST, int(DB_DSN_PORT), service_name=DB_DSN_SERVICE)

# Dados do BLiP
URLBLIP_COMMANDS = os.getenv("URLBLIP_COMMANDS")
URLBLIP_MESSAGES = os.getenv("URLBLIP_MESSAGES")
KEYBLIP = os.getenv("KEYBLIP")
TEMPLATE_NAME = os.getenv("TEMPLATE_NAME")
NAMESPACE = os.getenv("NAMESPACE")

app = Flask(__name__)

def get_whatsapp_identifier(phone):
    formatted_phone = f"+55{phone}"
    request_id = str(uuid.uuid4())

    payload = json.dumps({
        "id": request_id,
        "to": "postmaster@wa.gw.msging.net",
        "method": "get",
        "uri": f"lime://wa.gw.msging.net/accounts/{formatted_phone}"
    }).encode("utf-8")

    req = urllib_request.Request(URLBLIP_COMMANDS, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': KEYBLIP
    })

    try:
        with urllib_request.urlopen(req) as res:
            data = json.loads(res.read())
            return data['resource']['alternativeAccount']
    except Exception as e:
        logging.error(f"Erro ao buscar ID do cliente {phone}: {e}")
        return None

def send_notification(to, message_content):
    request_id = str(uuid.uuid4())

    payload = json.dumps({
        "id": request_id,
        "to": to,
        "type": "application/json",
        "content": {
            "type": "template",
            "template": {
                "namespace": NAMESPACE,
                "language": {"code": "pt_BR", "policy": "deterministic"},
                "name": TEMPLATE_NAME,
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": message_content}]
                }]
            }
        }
    }).encode('utf-8')

    req = urllib_request.Request(URLBLIP_MESSAGES, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': KEYBLIP
    })

    try:
        with urllib_request.urlopen(req) as res:
            return res.read().decode()
    except Exception as e:
        logging.error(f"Erro ao enviar para {to}: {e}")
        return str(e)

@app.route('/send_notification', methods=['POST'])
def process_and_send():
    connection = None
    results = []

    try:
        connection = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
        cursor = connection.cursor()

        query = """
        SELECT 
            abp.NR_SEQ_NOTIFICACAO,
            abp.DS_MENSAGEM AS text,
            CASE 
                WHEN LENGTH(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')) = 11 THEN
                    REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')
                WHEN LENGTH(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')) = 12 AND 
                    SUBSTR(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', ''), 1, 1) = '0' THEN
                    SUBSTR(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', ''), 2)
                WHEN LENGTH(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')) = 12 AND 
                    SUBSTR(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', ''), 3, 1) = '0' THEN
                    SUBSTR(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', ''), 1, 2) ||
                    SUBSTR(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', ''), 4)
                WHEN LENGTH(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')) = 9 THEN
                    '17' || REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')
                WHEN LENGTH(REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')) = 8 THEN
                    '179' || REGEXP_REPLACE(pf.NR_TELEFONE_CELULAR, '[^0-9]', '')
                ELSE NULL
            END AS phone
        FROM 
            API_BLIP_PAS abp
        JOIN 
            PLS_SEGURADO ps ON abp.NR_SEQ_SEGURADO = ps.NR_SEQUENCIA
        JOIN 
            PESSOA_FISICA pf ON ps.CD_PESSOA_FISICA = pf.CD_PESSOA_FISICA
        WHERE
            abp.CD_STATUS = 1
        """

        cursor.execute(query)
        for row in cursor:
            nr_sequencia, message, phone = row
            if not phone or not message:
                continue

            if hasattr(message, 'read'):
                message = message.read()

            identifier = get_whatsapp_identifier(phone)
            if identifier:
                response = send_notification(identifier, message)
                results.append({
                    "phone": phone,
                    "status": "sent",
                    "response": response
                })

                update_cursor = connection.cursor()
                update_query = "UPDATE API_BLIP_PAS SET CD_STATUS = 2 WHERE NR_SEQ_NOTIFICACAO = :1"
                update_cursor.execute(update_query, (nr_sequencia,))
                connection.commit()
                update_cursor.close()
            else:
                results.append({
                    "phone": phone,
                    "status": "failed",
                    "reason": "Invalid identifier"
                })

        logging.info(f"Notificações processadas: {results}")
        return jsonify(results)

    except Exception as e:
        logging.error(f"Erro durante o processamento: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
