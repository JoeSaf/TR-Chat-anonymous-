import os
import socket
import threading
import PUB_CON
import MSG_ENC
from Crypto.PublicKey import RSA

# Lock to ensure thread-safe access to clients and names
clients_lock = threading.Lock()
names_lock = threading.Lock()

def handle_client(client_socket, client_address, name, key):
    print(f"{name} connected successfully")
    
    with clients_lock:  # Ensuring only one thread modifies the clients list
        for c in clients:
            if c != client_socket:
                new_data = bytes("server<bl4km4n>" + name + " connected successfully", 'utf-8')
                new_enc_data = MSG_ENC.AES_256_ENCRYPT(key, new_data)
                c.sendall(new_enc_data)

    while True:
        try:
            data = client_socket.recv(1024)
            data = MSG_ENC.AES_256_DECRYPT(key, data)
            data = str(data, 'utf-8')
            
            if not data:
                break

            # Check for 'BYE' command to terminate connection
            if data.strip().upper() == "BYE":
                print(f"{name} sent 'BYE'. Closing connection.")
                break
            
            # Forward the message to other clients
            with clients_lock:  # Ensuring thread-safe access to clients
                for c in clients:
                    if c != client_socket:
                        new_data = bytes(name + "<bl4km4n>" + data, 'utf-8')
                        new_enc_data = MSG_ENC.AES_256_ENCRYPT(key, new_data)
                        c.sendall(new_enc_data)
        
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            break
    
    client_socket.close()

    with clients_lock:  # Ensuring thread-safe access to clients
        clients.remove(client_socket)

    # Notify other clients that this client has left
    with names_lock:  # Locking names to ensure consistency when updating
        for c in clients:
            leave_msg = "server<bl4km4n>" + name + " left this chat"
            new_leave_msg = MSG_ENC.AES_256_ENCRYPT(key, bytes(leave_msg, 'utf-8'))
            c.sendall(new_leave_msg)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 8089))

server_socket.listen(5)
get_key = PUB_CON.CRT_PUB_CON()
key = MSG_ENC.KEY_ENC(get_key)
ENC_KEY = MSG_ENC.GEN_AES_256_KEY()
print("Shared Key ::: {}".format(key))
print("Server is listening for incoming connections...")

clients = []
names = []

try:
    while True:
        client_socket, client_address = server_socket.accept()
        name = str(client_socket.recv(1024), 'utf-8')

        # Check if the name is already in use
        with names_lock:  # Locking names to avoid race conditions when checking
            if name in names:
                client_socket.send(bytes("avail", 'utf-8'))
                client_socket.close()
                continue

        # Automatically accept the connection (no user input needed)
        client_socket.send(bytes("accept", 'utf-8'))
        
        # Handle public key exchange and AES key encryption
        get_pub_key_str = str(client_socket.recv(1024), 'utf-8')
        public_key = RSA.import_key(get_pub_key_str)
        enc_enc_key = MSG_ENC.RSA_ENC(public_key, ENC_KEY)
        client_socket.send(enc_enc_key)

        with clients_lock:  # Ensuring thread-safe access to clients
            clients.append(client_socket)

        with names_lock:  # Locking names to ensure thread-safe modification
            names.append(name)

        # Start a thread to handle the client communication
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, name, ENC_KEY))
        client_thread.start()

except KeyboardInterrupt:
    print("Server shutting down...")
    with clients_lock:  # Ensuring thread-safe access to clients
        for client_socket in clients:
            client_socket.close()
    server_socket.close()
