#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import signal
import threading
from socket import *

clientes_exibicao = {} # Dicionário para armazenar os clientes de exibição (id: (endereço, tipo))
clientes_envio = {} # Dicionário para armazenar os clientes de envio (id: (endereço, tipo))

# Envia a mensagem identidade periódica.
def envio_msg_periodica(signum, frame):

# Retorna uma mensagem dizendo o número de clientes de envio e de exibição conectados ao servidor.
def criar_msg_identidade():

# Recebe a mensagem, divide entre mensagem e endereço e chama a função para processar a mensagem.
def processar_cliente():

# Decodifica a mensagem entre tipo, endereço do remetente, endereço do destinatário e o texto, de acordo com
# as especificações do trabalho.
def processar_msg(msg, end):

# Verifica se o cliente já está cadastrado como de envio ou de exibição, caso não esteja, de acordo com os endereços
# especificados no trabalho, registra como de envio ou de exibição.
def registrar_cliente(cliente_id, end):

# Deleta o cliente da lista de clientes de exibição ou de envio. Verificar na especificação do trabalho se precisa
# usar a lógica da mensagem TCHAU nessa situação.
def remover_cliente(cliente_id):

# Função para enviar a mensagem. Verifica se o remetente é válido. Se for 0, a msg deve ser enviada a todos os usuários
# Se não for 0, envia apenas para o destinatário especifico.
def enviar_msg(remetente_id, destino_id, texto):

# Configura o socket
# Configura o sinal para o envio de mensagens periódicas
# Inicia a thread para processar os clientes.
def main():

