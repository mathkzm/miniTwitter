#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import threading

# Fazer um loop.
# Lê a msg do usuário. Se for TCHAU, envia a msg para o servidor e sai do loop.
# Caso contrário, pede o ID do destinatário. (Se for 0, a mensagem é enviada para todos).
# Se o ID do destinatário não estiver no intervalo determinado pela especificação do trabalho -> ERRO.
# Envia a mensagem para o servidor.
def enviar_msg(sock, servidor_ip, servidor_porta, cliente_id):

# Função que recebe como parâmetros sock, IP do servidor, porta do servidor e ID do cliente e envia
# a mensagem de TCHAU.
def envia_tchau(sock, servidor_ip, servidor_port, cliente_id):

# Função que cria a mensagem de texto.
def criar_msg_texto(remetente_id, destino_id, texto):

# Função que cria a mensagem de TCHAU.
def criar_msg_tchau(cliente_id):

# Função que cria a mensagem de OI
def criar_msg_oi(cliente_id, username):

# Estabelecer a execução exatamente como o especificado no trabalho.
# python cliente_envio.py <ID> <nome_usuario> <endereço_servidor:porta
# Armazenar em variável o ID do cliente, o nome de usuário e o endereço do servidor.
# O endereço do servidor é dividido em IP e porta. Fazer um split a partir do : e armazenar nas variáveis de servidor IP e Porta do servidor.
# Inicializar o sock
# Envio da mensagem OI da inicialização.
# Recebimento da mensagem OI da inicialização.
# Elaborar lógica da THREAD de recebimento.
def main():

if __name__ == "__main__":
    main()