#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import threading
from socket import *
import logging

# Configuração de logging para o registro das entradas e saídas dos clientes
logging.basicConfig(filename='servidor_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Dicionários para armazenar os clientes
clientes_exibicao = {}  # {id: (endereço, tipo)}
clientes_envio = {}     # {id: (endereço, tipo)}
servidor_inicio = time.time()  # Para calcular o tempo de atividade do servidor

# Envia a mensagem de identidade periódica a cada 60 segundos.
def envio_msg_periodica():
    while True:
        time.sleep(60)  # Espera 60 segundos
        mensagem_identidade = criar_msg_identidade()
        # Envia a mensagem de identidade para todos os clientes de exibição
        for cliente in clientes_exibicao.values():
            endereco = cliente[0]
            enviar_msg(0, 0, mensagem_identidade, endereco)

# Retorna uma mensagem com o número de clientes conectados ao servidor e o tempo de atividade.
def criar_msg_identidade():
    num_envio = len(clientes_envio)
    num_exibicao = len(clientes_exibicao)
    tempo_ativo = time.time() - servidor_inicio
    tempo_formatado = time.strftime("%H:%M:%S", time.gmtime(tempo_ativo))
    return f"Identidade: {num_envio} clientes de envio, {num_exibicao} clientes de exibição. Servidor ativo há {tempo_formatado}."

# Recebe as mensagens dos clientes e processa conforme o tipo.
def processar_cliente():
    while True:
        try:
            msg, end = socket_cliente.recvfrom(1024)
            print(f"Mensagem recebida do cliente {end}: {msg.decode()}")
            processar_msg(msg.decode(), end)
        except (ConnectionResetError, OSError):
            # Trata desconexões inesperadas, remove o cliente da lista como se tivesse recebido TCHAU
            cliente_id = get_cliente_id_by_endereco(end)
            if cliente_id:
                remover_cliente(cliente_id)

# Obtém o cliente ID pelo endereço (caso de desconexão inesperada)
def get_cliente_id_by_endereco(end):
    for cliente_id, cliente_info in {**clientes_exibicao, **clientes_envio}.items():
        if cliente_info[0] == end:
            return cliente_id
    return None

# Decodifica a mensagem e a processa.
def processar_msg(msg, end):
    partes = msg.split()
    
    if len(partes) < 3:  # Verifica se a mensagem tem pelo menos 3 partes
        print(f"Mensagem malformada recebida de {end}: {msg}")
        return
    
    tipo = partes[0]
    remetente_id = int(partes[1])
    destino_id = int(partes[2])
    texto = " ".join(partes[3:])
    
    if tipo == "MSG":
        if remetente_id in {**clientes_exibicao, **clientes_envio}:
            enviar_msg(remetente_id, destino_id, texto, end)
        else:
            print(f"Mensagem ignorada de {end}: remetente não registrado.")
    elif tipo == "OI":
        registrar_cliente(remetente_id, end)
    elif tipo == "TCHAU":
        remover_cliente(remetente_id)

# Registra o cliente (envio ou exibição) e faz log da entrada.
def registrar_cliente(cliente_id, end):
    if cliente_id % 2 == 0:  # Exemplo de separação por ID par/ímpar
        clientes_exibicao[cliente_id] = (end, 'exibicao')
    else:
        clientes_envio[cliente_id] = (end, 'envio')
    logging.info(f"Cliente {cliente_id} (endereço: {end}) registrado.")

# Remove o cliente da lista de exibidores ou de envio, faz log da saída.
def remover_cliente(cliente_id):
    if cliente_id in clientes_exibicao:
        del clientes_exibicao[cliente_id]
        logging.info(f"Cliente de exibição {cliente_id} removido.")
    elif cliente_id in clientes_envio:
        del clientes_envio[cliente_id]
        logging.info(f"Cliente de envio {cliente_id} removido.")

# Envia a mensagem para um cliente ou para todos os exibidores.
def enviar_msg(remetente_id, destino_id, texto, endereco=None):
    if destino_id == 0:  # Envia para todos
        for cliente in clientes_exibicao.values():
            endereco_cliente = cliente[0]
            socket_cliente.sendto(f"MSG {remetente_id} {texto}".encode(), endereco_cliente)
    elif destino_id in clientes_exibicao:
        endereco_cliente = clientes_exibicao[destino_id][0]
        socket_cliente.sendto(f"MSG {remetente_id} {texto}".encode(), endereco_cliente)
    else:
        print(f"Cliente {destino_id} não encontrado.")

# Função principal para configurar o servidor e iniciar a comunicação
def main():
    global socket_cliente
    socket_cliente = socket(AF_INET, SOCK_DGRAM)
    socket_cliente.bind(('localhost', 12345))

    print("Servidor iniciado e aguardando mensagens...")

    # Cria uma thread para envio de mensagens periódicas
    threading.Thread(target=envio_msg_periodica, daemon=True).start()

    # Cria uma thread para processar novos clientes
    threading.Thread(target=processar_cliente, daemon=True).start()

    # Mantém o servidor rodando indefinidamente
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Servidor encerrado.")
        logging.info("Servidor encerrado.")

if __name__ == "__main__":
    main()
