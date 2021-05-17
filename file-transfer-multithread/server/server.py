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
    cmd, filename, filesize = received.split(SEPARATOR)
        
    filesize = int(filesize)
    remaining = filesize
    
    if os.path.isfile(filename):
        client_socket.send(str.encode("Erro: arquivo já existente."))
    else:
        with open(filename, "wb") as f:
            while True:
                if remaining <= 0:
                    break
                bytes_read = client_socket.recv(BUFFER_SIZE)

                f.write(bytes_read)

                remaining -= len(bytes_read)
                print(100*(filesize - remaining)/filesize, "%")
        client_socket.sendall(str.encode("Sucesso: arquivo recebido"))



def list_files(client_socket):
    print("list files")
    files = os.listdir()
    response = "Arquivos disponíveis:\n"
    for f in files:
        response += f + "\n"
    client_socket.sendall(str.encode(response))



def handle_client(client_socket, address):
    while True:
        # Recebendo os dados do cliente
        received = client_socket.recv(BUFFER_SIZE).decode()
        
        # Separando os dados recebidos para interpretar mensagem
        msg = received.split(SEPARATOR)
        
        cmd = msg[0]
        if cmd == "new":
            receive_file(received, client_socket)
        elif cmd == "ls":
            list_files(client_socket)
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