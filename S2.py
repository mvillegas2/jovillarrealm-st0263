import pika
from conf import configure
import json
import os, glob
import ops
def mom():

    conf = configure()
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
        files = None
        if payload["action"] == "list":
            print("List recibido")
            files = ops.list_files(conf["SUBDIR"])
            print(f"A enviar {files}")
        elif payload["action"] == "find":
            query = payload["query"]
            print(f"Find {query}")
            files = ops.find_files(conf["SUBDIR"],query)
            print(f"A enviar {files}")
        if files:
            channel.basic_publish(
                exchange=conf["RABBITMQ_EXCHANGE"],
                routing_key=conf["RABBITMQ_QUEUE_RESPONSE_KEY"],
                body=json.dumps(files),
            )


    channel.basic_consume(
        queue=conf["RABBITMQ_QUEUE_REQUEST"], on_message_callback=callback, auto_ack=True
    )
    print("Consumiendo")
    channel.start_consuming()
    

if __name__ == "__main__":
    mom()