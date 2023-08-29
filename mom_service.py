import pika
from conf import self_conf
import json
import os, glob
def mom():
    conf = self_conf()

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            conf["MOM_SERVER_IP"],
            conf["MOM_PORT"],
            "/",
            pika.PlainCredentials(conf["RABBITMQ_USER"], conf["RABBITMQ_PASSWORD"]),
        )
    )
    channel = connection.channel()


    def callback(ch, method, properties, body):
        """Procesar cada mensaje"""
        payload = json.loads(body)

        if payload["action"] == "list":
            print("List recibido")
            ops_dir = conf["SUBDIR"]
            files = []
            for dir in os.walk(ops_dir):
                path, subdirs, sub_files = dir
                for file in sub_files:
                    files.append(os.path.join(path, file))
            print(f"A enviar {files}")
        elif payload["action"] == "find":
            query = payload["query"]
            print(f"Find {query}")

            files = [
                file
                for file in glob.glob(os.path.join(conf["SUBDIR"], query))
                if os.path.isfile(file)
            ]
            print(f"A enviar {files}")
            channel.basic_publish(
                exchange=conf["RABBITMQ_EXCHANGE"],
                routing_key=conf["RABBITMQ_QUEUE_RESPONSE_KEY"],
                body=json.dumps(files),
            )


    channel.basic_consume(
        queue=conf["RABBITMQ_QUEUE_REQUEST"], on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    mom()