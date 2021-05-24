from _thread import *
import socket
import getopt
import sys
import os

def parse_args():
    # Lista de argumentos lida pelo sistema
    argv = sys.argv[1:]

    # Lista de argumentos que serão aceitos
    options = ["port="]

    port = ""

    try:
        arguments, values = getopt.getopt(argv, [], options)
        for arg, val in arguments:
            if arg == "--port":
                port = int(val)
    
    except getopt.error as err:
        print("Erro com os argumentos utilizados")
        print(str(err))
    except ValueError:
        print("ValueError: A porta deve ser um valor numérico")
        exit()
    
    return port



def receive_file(received, client_socket):
    print(received)
    cmd, filename, filesize = received.split(SEPARATOR)
        
    filesize = int(filesize)
    remaining = filesize
    
    filepath = os.path.join(os.getcwd(), "files", filename)
    
    aux = filepath
    i = 1
    while os.path.isfile(aux):
        aux = os.path.join(os.getcwd(), "files", str(i) + "-" + filename)
        i += 1
    filepath = aux
    
    with open(filepath, "wb") as f:
        while True:
            if remaining <= 0:
                break
            bytes_read = client_socket.recv(BUFFER_SIZE)

            f.write(bytes_read)

            remaining -= len(bytes_read)
            print(100*(filesize - remaining)/filesize, "%")
    client_socket.sendall(str.encode("Sucesso: arquivo enviado"))


def list_files(client_socket):
    print("list files")
    files = os.listdir(os.path.join(os.getcwd(), "files"))
    response = "Arquivos disponíveis:\n"
    for f in files:
        response += f + "\n"
    client_socket.sendall(str.encode(response))


def send_files(received, client_socket):
    msg = received.split(SEPARATOR)
    
    filename = msg[1]
    filepath = os.path.join(os.getcwd(), "files", filename)

    filesize = 0

    try:
        filesize = os.path.getsize(filepath)
    except FileNotFoundError as e:
        client_socket.send(str.encode("Erro: arquivo não encontrado"))
        return

    client_socket.send(f"{filename}{SEPARATOR}{filesize}".encode())

    sent = 0
    print("Enviando...")
    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if len(bytes_read) <= 0:
                break
            
            client_socket.sendall(bytes_read)

            sent += len(bytes_read)
            print(100*sent/filesize, "%")
    
    res = client_socket.recv(BUFFER_SIZE)
    print(res.decode('utf-8'))


def handle_client(client_socket, address):
    while True:

        try:
            # Recebendo os dados do cliente
            received = client_socket.recv(BUFFER_SIZE).decode()
        except ConnectionAbortedError as err:
            return
        
        # Separando os dados recebidos para interpretar mensagem
        msg = received.split(SEPARATOR)

        cmd = msg[0]
        if cmd == "new":
            receive_file(received, client_socket)
        elif cmd == "ls":
            list_files(client_socket)
        elif cmd == "get":
            send_files(received, client_socket)
        elif cmd == "stop":
            client_socket.close()
            break
        else:
            client_socket.send(str.encode("Erro: comando inválido"))
    
    print("out")




def main():
    # Criando socket
    try:
        s = socket.socket()
        s.bind((SERVER_HOST, SERVER_PORT))
    except socket.error as err:
        print("Erro ao criar socket")
        print(str(err))
        exit()

    s.listen(5)
    print(f"[*] Escutando em {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, address = s.accept()
        print(f"[+] {address} is connected.")
        start_new_thread(handle_client, (client_socket, address))



# Leitura dos argumentos passados para o programa
port = parse_args()

# Constantes de configuração do servidor
SERVER_HOST = "0.0.0.0"
SERVER_PORT = port or 5050
BUFFER_SIZE = 4096
SEPARATOR = "###"

# Início do programa
main()