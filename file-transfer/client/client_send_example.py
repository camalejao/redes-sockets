import socket
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

host = "127.0.0.1"

port = 5050

filepath = input("Olá! Informe o caminho absoluto do arquivo que será enviado (ou apenas seu nome, caso esteja no mesmo diretório):\n")
filename = input("Informe com qual nome esse arquivo será salvo no servidor: ")

# NEW_PATH = input("Informe o caminho que o arquivo deve ser enviado: ")
NEW_PATH = ""

filesize = os.path.getsize(filepath)

s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

s.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{NEW_PATH}".encode())

progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filepath, "rb") as f:
    while True:
        bytes_read = f.read(BUFFER_SIZE)
        if len(bytes_read) <= 0:
            break
        
        s.sendall(bytes_read)
    
        progress.update(len(bytes_read))
s.close()