import socket
import tqdm
import os

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5050
BUFFER_SIZE = 4096

SEPARATOR = "<SEPARATOR>"

s = socket.socket()

s.bind((SERVER_HOST, SERVER_PORT))

s.listen(5)
print(f"[*] Escutando em {SERVER_HOST}:{SERVER_PORT}")

client_socket, address = s.accept()
print(f"[+] {address} is connected.")

received = client_socket.recv(BUFFER_SIZE).decode()
filename, filesize, NEW_PATH = received.split(SEPARATOR)

NEW_PATH = NEW_PATH+"\\"+filename

filesize = int(filesize)

progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

with open(NEW_PATH, "wb") as f:
    while True:
        bytes_read = client_socket.recv(BUFFER_SIZE)
        if not bytes_read:
            break

        f.write(bytes_read)

        progress.update(len(bytes_read))

client_socket.close()

s.close()