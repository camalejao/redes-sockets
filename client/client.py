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

# Função para listar os arquivos disponíveis no servidor
def list_files(s):
    s.send(f"ls{SEPARATOR}".encode())
    res = s.recv(BUFFER_SIZE)
    print(res.decode('utf-8'))

# Função para enviar arquivos do cliente ao servidor
def send_file(s):
    # Recebemos a entrada do cliente
    filepath = input("Informe o caminho absoluto do arquivo que será enviado (ou apenas seu nome, caso esteja no mesmo diretório. Obs: não esqueça a extensão do arquivo):\n")
    filename = input("\nInforme com qual nome esse arquivo será salvo no servidor: ")

    filesize = 0

    # verificamos se o arquivo existe
    try:
        filesize = os.path.getsize(filepath)
    except FileNotFoundError as e:
        print("\nErro: Não conseguimos encontrar o arquivo informado\n\n")
        return

    # Comunicamos ao servidor que enviaremos um novo arquivo
    s.send(f"new{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode())

    # Aguardamos a confirmação do servidor
    res = s.recv(BUFFER_SIZE)
    if res.decode('utf8') == 'clear':
        print("Enviando...")

    # Abrimos o arquivo e a medida que lemos seus bytes, os enviamos pelo socket
    sent = 0
    with open(filepath, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if len(bytes_read) <= 0:
                break
            
            s.sendall(bytes_read)

            sent += len(bytes_read)
            print(100*sent/filesize, "%")
    
    # Aguardamos a confirmação do servidor que o arquivo foi recebido
    res = s.recv(BUFFER_SIZE)
    print(res.decode('utf-8'))


# Função para realizar download de arquivos localizados no servidor
def download_files(s):
    # Primeiramente listamos os arquivos disponíveis
    list_files(s)

    # Recebemos a entrada do usuário com o nome do arquivo desejado
    filename = input("Informe o nome do arquivo: ")

    # Enviamos a requisição para o arquivo
    s.send(f"get{SEPARATOR}{filename}".encode())

    # Recebemos do servidor os detalhes do arquivo
    received = s.recv(BUFFER_SIZE).decode()
    try:
        filename, filesize = received.split(SEPARATOR)
    except ValueError:
        print(received)
        print("O arquivo requisitado não existe no servidor\n\n")
        return

    filesize = int(filesize)
    remaining = filesize

    # Caso ja exista arquivo com esse nome, é adicionado um prefixo indicando o número da cópia
    aux = filename
    i = 1
    while os.path.isfile(aux):
        aux = str(i) + "-" + filename
        i += 1
    filename = aux

    # Sinalizamos para o servidor realizar o envio do arquivo
    s.send("clear".encode())

    # Abrimos o arquivo e escrevemos o bytes a medida que eles são lidos pelo socket
    with open(filename, "wb") as f:
        while True:
            if remaining <= 0:
                break
            bytes_read = s.recv(BUFFER_SIZE)

            f.write(bytes_read)

            remaining -= len(bytes_read)
            print(100*(filesize - remaining)/filesize, "%")
    
    # Ao término da escrita, sinalizamos o sucesso da operação ao servidor e ao usuário
    msg = "Sucesso: arquivo recebido\n\n"
    s.send(str.encode(msg))
    print(msg)

        
    
def main():
    # Criamos o socket do lado do cliente
    s = socket.socket()
    s.connect((HOST, PORT))

    # Menu de opções para as funcionalidades do programa
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
            # Para sair, comunicamos o encerramento da execução do cliente
            s.sendall(f"stop{SEPARATOR}".encode())
    # Antes de encerrar, fechamos o socket aberto
    s.close()

# Leitura dos argumentos passados para o programa
ip, port = parse_args()

# Constantes de configuração do cliente
SEPARATOR = "###" # separador utilizado nas mensagens do protocolo criado
BUFFER_SIZE = 4096
HOST = ip or "127.0.0.1"
PORT = port or 5050

# Início do programa
main()