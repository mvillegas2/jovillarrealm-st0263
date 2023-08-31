import os, json
from dotenv import dotenv_values


def json_conf() -> dict[str, str]:
    file = os.path.join(os.getcwd(), "configure.json")
    with open(file) as jsconf:
        conf: dict = json.load(jsconf)
    return conf


def configure()->dict[str,str]:
    m = dotenv_values(".env")
    if not m:
        raise ValueError("sin .env")
    check = {
        "RPC_PORT": "50051",
        "MOM_PORT": "5672",
        "API_GATEWAY_IP": "35.175.18.22",
        "SERVICE_1_IP": "35.153.228.44",
        "SERVICE_2_IP": "18.215.116.134",
        "MOM_SERVER_IP": "52.22.134.153",
        "RABBITMQ_USER": "user",
        "RABBITMQ_PASSWORD": "password",
        "RABBITMQ_EXCHANGE": "filexchange",
        "RABBITMQ_QUEUE_REQUEST": "file_request",
        "RABBITMQ_QUEUE_REQUEST_KEY": "req",
        "RABBITMQ_QUEUE_RESPONSE": "file_response",
        "RABBITMQ_QUEUE_RESPONSE_KEY": "res",
        "SUBDIR": "files",
    }
    for i in check:
        if i not in m:
            raise ValueError("No existe la variable de entorno")
    return m