#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading
import struct

# Função para receber mensagens.
# Divide os campos da mensagem e encaminha a mensagem para a função de exibir.
def receber_msgs(sock):
    while True:
        try:
            msg, _ = sock.recvfrom(1024)
            exibir_msg(msg)
        except socket.error as e:
            print("Erro ao receber mensagem: {e}")
            
# Elaborar a função da decodificação de mensagens nos campos especificados (ID, remetente, destinatário, texto)
def decodificar_msg(msg):
    tipo, id_remetente, id_destino, tam_texto = struct.unpack('!4i', msg[:16])
    nome_usuario = msg[16:36].decode().strip('\x00')  # Nome do usuário com 20 caracteres
    texto = msg[36:36 + tam_texto].decode().strip('\x00')  # Texto da mensagem
    return tipo, id_remetente, id_destino, nome_usuario, texto
    
# Função de exibir mensagens.
# Decodifica a mensagem em tipo, remetente, destinatário e o texto.
# Verifica se o destinatário é 0 (exibir a todos). Nesse caso, especificar no print que é uma msg pública.
# Se o destinatário for diferente de 0, especificar que a msg é privada e colocar o destinatário.
def exibir_msg(msg):
    tipo, id_remetente, id_destino, nome_usuario, texto = decodificar_msg(msg)

    if id_destino == 0: # Envia a mensagem para todos.
        print(f"[Todos] from {nome_usuario} ID {id_remetente}: {texto}")
    else: # Envia a mensagem privada.
        print(f"[Privado] from {nome_usuario} ID {id_remetente} to {id_destino}: {texto}")

# Cria o envio da mensagem OI com o registro do ID do cliente.
def criar_msg_oi(id_cliente):
    tipo = 0
    destino = 0 # Ela vai para o servidor.
    texto = ""
    nome_usuario = "ClienteExibicao"
    mensagem = f"{tipo} {id_cliente} {destino} {len(texto)} {nome_usuario}"
    return mensagem.encode()

# Estabelecer a execução exatamente como o especificado no trabalho.
# python cliente_exibicao.py <ID> <nome_usuario> <endereço_servidor:porta
# Armazenar em variável o ID do cliente, o nome de usuário e o endereço do servidor.
# O endereço do servidor é dividido em IP e porta. Fazer um split a partir do : e armazenar nas variáveis de servidor IP e Porta do servidor.
# Inicializar o sock
# Envio da mensagem OI da inicialização.
# Recebimento da mensagem OI da inicialização.
# Elaborar lógica da THREAD de recebimento.
def main():
    if len(sys.argv) != 3:
        print("Uso correto: python cliente_exibicao.py <ID> <endereço_servidor:porta>")
        sys.exit(1)
    else:
        id_cliente = int(sys.argv[1])
        end_servidor = sys.argv[2].split(":")
        ip_servidor = end_servidor[0]
        porta_servidor = int(end_servidor[1])

        # Criação do socket UDP
        sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Criação da mensagem OI para iniciar a conexão com o servidor.
        msg_oi = criar_msg_oi(id_cliente)
        sockUDP.sendto(msg_oi,(ip_servidor, porta_servidor))

        print("Solicitação de conexão inicial enviada ao servidor.")

        # Espera pela resposta da solicitação
        resposta, _ = sockUDP.recvfrom(1024)
        tipo, remetente_id, destino_id, texto = decodificar_msg(resposta)

        if tipo == 0: # Recebeu OI de volta
            print(f"Cliente de exibição {id_cliente} registrado com sucesso no servidor.")
            # Thread usada para receber mensagens do servidor.
            threading.Thread(target=receber_msgs,args=(sockUDP,),daemon=True).start()

            # Mantendo o cliente em execução.
            while True:
                pass
        else:
            print("Erro ao registrar o cliente de exibição.")

main()