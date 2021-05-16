import os
import socket
from _thread import *

def handle_client(connection, address):
    connection.send(str.encode('Servidor funcionando'))
    while True:
        data = connection.recv(2048)
        if not data:
            break
        msg = data.decode('utf-8')
        print('Mensagem recebida de', address[0] + ':' + str(address[1]), msg)
        response = 'Resposta ' + msg.upper()
        connection.sendall(str.encode(response))
    connection.close()

def main():
    server_socket = socket.socket()
    host = '127.0.0.1'
    port = 5050

    try:
        server_socket.bind((host, port))
    except socket.error as e:
        print('Não foi possível criar o socket do servidor.')
        print(str(e))

    # aguarda esse numero de conexoes 'nao aceitas' antes de recusar novas conexoes
    server_socket.listen(5)
    print('Servidor escutando na porta', port)

    while True:
        client, address = server_socket.accept()
        print('Conexao de', address[0] + ':' + str(address[1]))
        start_new_thread(handle_client, (client, address))
    
    server_socket.close()

main()