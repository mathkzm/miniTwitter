#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading

# Função que cria a mensagem de texto.
def criar_msg_texto(remetente_id, destino_id, texto):
    return f"MSG {remetente_id} {destino_id} {texto}"

# Função que cria a mensagem de TCHAU.
def criar_msg_tchau(cliente_id):
    return f"TCHAU {cliente_id}"

# Função que cria a mensagem de OI
def criar_msg_oi(cliente_id, username):
    return f"OI {cliente_id} {username}"

# Função que envia a mensagem.
def enviar_msg(sock, servidor_ip, servidor_porta, cliente_id):
    while True:
        msg = input("Digite sua mensagem (ou 'TCHAU' para sair): ")
        if msg == "TCHAU":
            mensagem_tchau = criar_msg_tchau(cliente_id)
            sock.sendto(mensagem_tchau.encode(), (servidor_ip, servidor_porta))
            break
        else:
            destino_id = int(input("Digite o ID do destinatário (0 para todos): "))
            if destino_id < 0:  # Verifica se o ID do destinatário é válido
                print("ERRO: O ID do destinatário deve ser um número positivo.")
                continue
            mensagem = criar_msg_texto(cliente_id, destino_id, msg)
            sock.sendto(mensagem.encode(), (servidor_ip, servidor_porta))
            print(f"Enviando mensagem: {mensagem}")

# Recebendo mensagens do servidor em uma thread separada
def receber_respostas(sock):
    while True:
        try:
            msg, end = sock.recvfrom(1024)
            print(f"Mensagem recebida: {msg.decode()} de {end}")
        except Exception as e:
            print(f"Ocorreu um erro ao receber a mensagem: {e}")
            break

# Estabelecer a execução exatamente como o especificado no trabalho.
# python cliente_envio.py <ID> <nome_usuario> <endereço_servidor:porta>
def main():
    if len(sys.argv) != 4:
        print("Uso: python3 cliente_envio.py <ID> <nome_usuario> <endereço_servidor:porta>")
        sys.exit(1)

    cliente_id = int(sys.argv[1])
    username = sys.argv[2]
    servidor_info = sys.argv[3].split(':')
    servidor_ip = servidor_info[0]
    servidor_porta = int(servidor_info[1])

    # Inicializando o socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Envio da mensagem OI da inicialização
    mensagem_oi = criar_msg_oi(cliente_id, username)
    sock.sendto(mensagem_oi.encode(), (servidor_ip, servidor_porta))
    
    # Recebendo mensagens do servidor em uma thread separada
    threading.Thread(target=receber_respostas, args=(sock,), daemon=True).start()

    # Chama a função para enviar mensagens
    enviar_msg(sock, servidor_ip, servidor_porta, cliente_id)

if __name__ == "__main__":
    main()
