#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading

# Função para receber mensagens.
# Divide os campos da mensagem e encaminha a mensagem para a função de exibir.
def receber_msgs(sock):
    while True:
        msg, _ = sock.recvfrom(1024)
        exibir_msg(msg)

# Elaborar a função da decodificação de mensagens nos campos especificados (ID, remetente, destinatário, texto)
def decodificar_msg(msg):
    segmentos_msg = msg.decode().split(" ")
    tipo = int(segmentos_msg[0])
    id_remetente = int(segmentos_msg[1])
    id_destino = int(segmentos_msg[2])
    texto = segmentos_msg[3] if len(segmentos_msg) > 3 else "" # Mensagens de OI e TCHAU não contêm texto.
    return tipo, id_remetente, id_destino, texto
    
# Função de exibir mensagens.
# Decodifica a mensagem em tipo, remetente, destinatário e o texto.
# Verifica se o destinatário é 0 (exibir a todos). Nesse caso, especificar no print que é uma msg pública.
# Se o destinatário for diferente de 0, especificar que a msg é privada e colocar o destinatário.
def exibir_msg(msg):
    tipo, id_remetente, id_destino, texto = decodificar_msg(msg)

    if id_destino == 0: # Envia a mensagem para todos.
        print(f"[Todos] from {id_remetente}: {texto}")
    else: # Envia a mensagem privada.
        print(f"[Privado] from {id_remetente} to {id_destino}: {texto}")

# Cria o envio da mensagem OI
def criar_msg_oi(id_cliente, nome_usuario):
    tipo = 0
    return f"{tipo} {id_cliente} {nome_usuario}".encode()


# Estabelecer a execução exatamente como o especificado no trabalho.
# python cliente_exibicao.py <ID> <nome_usuario> <endereço_servidor:porta
# Armazenar em variável o ID do cliente, o nome de usuário e o endereço do servidor.
# O endereço do servidor é dividido em IP e porta. Fazer um split a partir do : e armazenar nas variáveis de servidor IP e Porta do servidor.
# Inicializar o sock
# Envio da mensagem OI da inicialização.
# Recebimento da mensagem OI da inicialização.
# Elaborar lógica da THREAD de recebimento.
def main():

if __name__ == "__main__":
    main()