import socket
import getopt
import sys
import os

def parse_args():
    # Lista de argumentos passada para o script
    argv = sys.argv[1:]

    # Lista de argumentos que serão aceitos
    options = ["ip=", "port="]

    ip = ""
    port = ""

    try:
        arguments, values = getopt.getopt(argv, [], options)
        for arg, val in arguments:
            if arg == "--ip":
                ip = val
            if arg == "--port":
                port = int(val)
    
    except getopt.error as err:
        print("Erro com os argumentos utilizados")
        print(str(err))
    except ValueError:
        print("ValueError: A porta deve ser um valor numérico")
        exit()
    
    return ip, port

def list_files(s):
    s.send(f"ls{SEPARATOR}".encode())
    res = s.recv(BUFFER_SIZE)
    print(res.decode('utf-8'))
    
def send_file(s):
    filepath = input("Olá! Informe o caminho absoluto do arquivo que será enviado (ou apenas seu nome, caso esteja no mesmo diretório. Obs: não esqueça a extensão do arquivo):\n")
    filename = input("Informe com qual nome esse arquivo será salvo no servidor: ")

    filesize = 0

    try:
        filesize = os.path.getsize(filepath)
    except FileNotFoundError as e:
        print("Não conseguimos encontrar o arquivo informado")
        return

    s.send(f"new{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode())

    res = s.recv(BUFFER_SIZE)
    if res.decode('utf8') == 'clear':
        print("Enviando...")

    sent = 0
    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if len(bytes_read) <= 0:
                break
            
            s.sendall(bytes_read)

            sent += len(bytes_read)
            print(100*sent/filesize, "%")
    
    res = s.recv(BUFFER_SIZE)
    print(res.decode('utf-8'))

def download_files(s):
    list_files(s)

    filename = input("Informe o nome do arquivo: ")

    s.send(f"get{SEPARATOR}{filename}".encode())

    received = s.recv(BUFFER_SIZE).decode()

    filename, filesize = received.split(SEPARATOR)

    filesize = int(filesize)
    remaining = filesize

    aux = filename
    i = 1
    while os.path.isfile(aux):
        aux = str(i) + "-" + filename
        i += 1
    filename = aux

    s.send("clear".encode())

    with open(filename, "wb") as f:
        while True:
            if remaining <= 0:
                break
            bytes_read = s.recv(BUFFER_SIZE)

            f.write(bytes_read)

            remaining -= len(bytes_read)
            print(100*(filesize - remaining)/filesize, "%")
    msg = "Sucesso: arquivo recebido"
    s.send(str.encode(msg))
    print(msg)

        
    
def main():
    s = socket.socket()
    s.connect((HOST, PORT))

    opt = 999
    while opt != 0:
        print("Opções:")
        print("[0] Sair")
        print("[1] Listar arquivos no servidor")
        print("[2] Enviar arquivo")
        print("[3] Baixar arquivo")
    
        opt = int(input())
        if opt == 1:
            list_files(s)
        elif opt == 2:
            send_file(s)
        elif opt == 3:
            download_files(s)
        elif opt == 0:
            s.sendall(f"stop{SEPARATOR}".encode())
    s.close()


ip, port = parse_args()
SEPARATOR = "###"
BUFFER_SIZE = 4096
HOST = ip or "127.0.0.1"
PORT = port or 5050

main()