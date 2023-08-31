from flask import Flask, jsonify
import json
import grpc
import files_pb2
import files_pb2_grpc
import pika
from conf import self_conf

# python -m grpc_tools.protoc -I ./protobufs --python_out=. --pyi_out=. --grpc_python_out=. ./protobufs/files.proto

conf = self_conf()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def faulting():
    return "<h1>Howdy</h1>"


@app.route("/list_files", methods=["GET"])
def list_files():
    directive = "list"
    try:
        files = rp_call(conf, directive)
    except:
        try:
            files = MO_call(conf, directive)
        except:
            files = []
    print(f"A enviar {files}")
    return jsonify(files)


@app.route("/find_files/<path:query>", methods=["GET"])
def find_files(query):
    directive = "find"
    try:
        files = rp_call(conf, directive, query)
        pass
    except:
        try:
            files = MO_call(conf, directive,query)
        except:
            files = []
    print(f"A enviar {files}")
    return jsonify(files)


def rp_call(conf: dict, pc: str, param=None) -> list[str]:
    # channel = grpc.secure_channel(ms_IP+":50051", grpc.ssl_channel_credentials(conf["pem"]))
    channel = grpc.insecure_channel(conf["SERVICE_1_IP"] + ":" + conf["RPC_PORT"])
    stub = files_pb2_grpc.RPStub(channel)

    if pc == "list":
        empty_msg = files_pb2_grpc.google_dot_protobuf_dot_empty__pb2.Empty()
        response = list(stub.ListFiles(empty_msg).files)
    elif pc == "find" and param is not None:
        print(f"param: {param}")
        query = files_pb2.Query(file=param)
        response = list(stub.FindFiles(query).files)
    else:
        print("WHAT")
        response = []
    return response


def MO_call(conf: dict, pc: str, param=None):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            conf["MOM_SERVER_IP"],
            conf["MOM_PORT"],
            "/",
            pika.PlainCredentials(conf["RABBITMQ_USER"], conf["RABBITMQ_PASSWORD"]),
        )
    )
    response = None
    try:
        pc = json.dumps({"action": pc, "query": param})
        channel = connection.channel()
        channel.basic_publish(
            exchange=conf["RABBITMQ_EXCHANGE"],
            routing_key=conf["RABBITMQ_QUEUE_REQUEST_KEY"],
            body=pc,
        )
        def callback(ch, method, properties, body):
            print(body)
            files = body
        method, properties, body = channel.basic_get(queue=conf["RABBITMQ_QUEUE_RESPONSE"], auto_ack=True)
        if body:
            response = json.loads(body)
        connection.close()
    except:
        connection.close()

    return response




if __name__ == "__main__":
    app.run(host="0.0.0.0")
