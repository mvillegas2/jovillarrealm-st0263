import grpc
from concurrent import futures
import os, glob
import grpc

import files_pb2
import files_pb2_grpc

from conf import self_conf

# TODO MOM, readme
conf = self_conf()
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    files_pb2_grpc.add_RPServiceServicer_to_server(RPService(), server)
    server.add_insecure_port("0.0.0.0" + ":" + conf["RPC_PORT"])
    print("Service is running... ")
    server.start()
    server.wait_for_termination()


class RPService(files_pb2_grpc.RPServiceServicer):
    def ListFiles(self, request, context):
        print("List recibido")
        ops_dir = conf["SUBDIR"]
        files = []
        for dir in os.walk(ops_dir):
            path, subdirs, sub_files = dir
            for file in sub_files:
                files.append(os.path.join(path,file))
        print(f"A enviar {files}")


        return files_pb2.FileList(files=files)

    def FindFiles(self, request, context):
        print(f"Request {request}")
        print(f"Context {context}")
        query =  str(request.file)
        print(query)
        files = [
            file
            for file in glob.glob(os.path.join(conf["SUBDIR"], query))
            if os.path.isfile(file)
        ]
        print(f"A enviar {files}")
        return files_pb2.FileList(files=files)

if __name__ == "__main__":
    serve()
    