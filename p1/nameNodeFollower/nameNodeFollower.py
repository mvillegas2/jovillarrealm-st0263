from flask import Flask, request, jsonify, redirect, Response
import grpc
import file_pb2
import file_pb2_grpc
import threading
import time
from itertools import cycle
import requests

import environs

env = environs.Env()
env.read_env()
server_addresses = env.list("DATANODES")
grpc_addresses = env.list("GRPC_DATANODES")

app = Flask(__name__)
print(server_addresses)
print(grpc_addresses)
# List of server addresses for round-robin load balancing
# server_addresses = ['localhost:50051', 'localhost:50052', 'localhost:50053']
#server_addresses = ['127.0.0.2:50051', '127.0.0.3:50051']

current_server_index = 0  # Initialize the index to the first server
file_lists = {}  # Dictionary to store the file lists for each server

def check_other_server_health():
    other_server_url = f"http://{env('NAME_NODE')}:8080/list"  # Replace with the URL of the other server
    try:
        response = requests.get(other_server_url)
        if response.status_code != 200:
            return False
    except requests.RequestException:
        return False
    return True
def monitor_other_server():
    while True:
        if not check_other_server_health():
            print("The other server is not healthy. Taking over...")
            # Start a background thread to periodically update the file lists
            update_interval = 60  # Update every 60 seconds (adjust as needed)
            update_thread = threading.Thread(target=periodic_file_list_update, args=(update_interval,))
            update_thread.daemon = True
            update_thread.start()
            # Add your code here to handle taking over the functionality
            # For example, you can start serving as a replacement
            # by running the necessary server logic.
        else:
            print("The other server is healthy.")
        time.sleep(15)  # Adjust the interval as needed
def get_server():
    addresses = cycle(server_addresses)
    for server_address in addresses:
        yield server_address


def change_port(input_string, new_port):
    # Split the input string into IP and port
    ip, old_port = input_string.split(':')

    # Create a new string with the same IP and the new port
    new_string = f"{ip}:{new_port}"

    return new_string


def get_next_server(private=False):
    global current_server_index
    # Get the next server address in a round-robin fashion
    if not private:
        server_address = server_addresses[current_server_index]
    else:
        server_address = grpc_addresses[current_server_index]
    current_server_index = (current_server_index + 1) % len(server_addresses)
    return server_address


def create_stub(server_address):
    # Create a gRPC stub for the specified server address
    channel = grpc.insecure_channel(server_address)
    return file_pb2_grpc.FileServiceStub(channel)


def update_file_list(server_address):
    try:
        stub = create_stub(server_address)
        response = stub.ListFiles(file_pb2.Empty())
        if response.filenames:
            file_lists[server_address] = response.filenames
        else:
            file_lists[server_address] = []
        
    except grpc.RpcError as e:
        print(f"Error listing files from {server_address}: {e.details()}")


def periodic_file_list_update(interval):
    while True:
        for server_address in grpc_addresses:
            update_file_list(server_address)
        print(file_lists)
        time.sleep(interval)




@app.route('/uploadserver/', methods=['GET'])
def upload_server():
    try:
        # Determine the appropriate DataNode server based on the filename
        server_address = get_next_server()
        server_address = change_port(server_address, 8080)
        # Construct the full URL of the DataNode server
        response ={"server_url" : f"http://{server_address}/upload/"}
        # Respond the client's browser to the server URL
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f"Error uploading file: {str(e)}"})

@app.route('/upload/<filename>', methods=['POST'])
def upload_file(filename):
    try:
        server_address = get_next_server()
        server_address = change_port(server_address, 8080)
        # Construct the full URL of the DataNode server
        server_url = f"http://{server_address}/upload/{filename}"
        # Forward the POST request to the target server
        response = requests.post(
            f"{server_url}",
            data=request.data,
            headers=request.headers
        )
        r = Response(response.content, status=response.status_code)

        # Determine the appropriate DataNode server based on the filename
        # Return the response from the target server to the client
        return r
    except Exception as e:
        return jsonify({'error': f"Error uploading file: {str(e)}"})


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Determine the appropriate DataNode server based on the filename
        server_address = get_server_for_file(filename)
        if not server_address:
            return jsonify({'error': f"File {filename} not found on any server."})

        server_address = change_port(server_address, 8080)

        # Construct the full URL of the DataNode server
        server_url = f"http://{server_address}/download/{filename}"

        # Redirect the client's browser to the server URL
        return redirect(server_url)

    except Exception as e:
        return jsonify({'error': f"Error downloading file: {str(e)}"})


# Helper function to get the DataNode server for a given filename
def get_server_for_file(filename):
    for server_address in grpc_addresses:
        if server_address in file_lists and filename in file_lists[server_address]:
            return server_addresses[grpc_addresses.index(server_address)]
    return None


def eliminate_duplicates(input_list):
    # Create an empty set to store unique elements
    unique_set = set()

    # Create a new list to store the unique elements in the original order
    unique_list = []

    # Iterate through the input list
    for item in input_list:
        # If the item is not in the set, it's unique
        if item not in unique_set:
            unique_set.add(item)
            unique_list.append(item)

    return unique_list


@app.route('/list', methods=['GET'])
def list_files():
    try:
        # Aggregate the file lists from all servers into one unified list
        all_files = []
        
        for server_address in grpc_addresses:
            if server_address in file_lists:
                all_files.extend(file_lists[server_address])
        all_files = eliminate_duplicates(all_files)

        if all_files:
            return jsonify({'files': all_files})
        else:
            return jsonify({'message': 'No files found on any server.'})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    #app.run(port=8080)
    monitor_thread = threading.Thread(target=monitor_other_server)
    monitor_thread.daemon = True
    monitor_thread.start()
    app.run(host=env('SELF_IP'),port=8080)
