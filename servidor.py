#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import threading
from socket import *
import logging
import struct

# Configuração de logging para o registro das entradas e saídas dos clientes
logging.basicConfig(filename='servidor_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
            processar_msg(msg, end)
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
    try:
        # Desempacota a mensagem de acordo com o seu tamanho
        tipo_msg, remetente_id, destino_id, tamanho = struct.unpack('!iiii', msg[:16])  # Apenas o cabeçalho
        texto = msg[16:].decode().rstrip('\0')  # O restante da mensagem após o cabeçalho
    except struct.error as e:
        print(f"Erro ao processar a mensagem recebida de {end}: {msg}")
        print(f"Detalhes do erro: {e}")
        return

    if tipo_msg == 0:  # OI
        registrar_cliente(remetente_id, end, texto)  # Passa o nome de usuário
        # Envia a mensagem "OI" de volta para o cliente que acabou de se registrar
        socket_cliente.sendto(f"OI {remetente_id} 0 OI".encode(), end)
        logging.info(f"Mensagem 'OI' enviada de volta para o cliente {remetente_id}.")
    elif tipo_msg == 1:  # MSG
        if remetente_id in {**clientes_exibicao, **clientes_envio}:
            enviar_msg(remetente_id, destino_id, texto, end)
        else:
            print(f"Mensagem ignorada de {end}: remetente não registrado.")
    elif tipo_msg == 2:  # TCHAU
        remover_cliente(remetente_id)

# Registra o cliente (envio ou exibição) e faz log da entrada.
def registrar_cliente(remetente_id, end, username):
    # Verificação de IDs de exibição e envio
    if 1 <= remetente_id <= 999:
        # Cliente de exibição: precisa garantir que nem o ID e nem (ID+1000) estejam em uso
        if remetente_id in clientes_exibicao or (remetente_id + 1000) in clientes_envio:
            socket_cliente.sendto(f"ERRO {remetente_id} Identificador já em uso".encode(), end)
            logging.error(f"Registro de cliente de exibição falhou: ID {remetente_id} já em uso.")
            return
        else:
            clientes_exibicao[remetente_id] = (end, username)
            logging.info(f"Cliente de exibição registrado: {remetente_id} - {username} ({end})")

    elif 1001 <= remetente_id <= 1999:
        # Cliente de envio: garantir que o ID não está em uso
        if remetente_id in clientes_envio:
            socket_cliente.sendto(f"ERRO {remetente_id} Identificador já em uso".encode(), end)
            logging.error(f"Registro de cliente de envio falhou: ID {remetente_id} já em uso.")
            return
        else:
            clientes_envio[remetente_id] = (end, username)
            logging.info(f"Cliente de envio registrado: {remetente_id} - {username} ({end})")
    
    else:
        # Se o ID estiver fora do intervalo esperado, enviar mensagem de erro
        socket_cliente.sendto(f"ERRO {remetente_id} Identificador inválido".encode(), end)
        logging.error(f"Tentativa de registro com ID inválido: {remetente_id}")
        return

    # Envia a confirmação de OI de volta para o cliente
    socket_cliente.sendto(f"OI {remetente_id} 0 OI".encode(), end)
    logging.info(f"Mensagem 'OI' enviada de volta para o cliente {remetente_id}.")


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
            mensagem = criar_msg_texto(remetente_id, 0, texto)
            socket_cliente.sendto(mensagem, endereco_cliente)
    elif destino_id in clientes_exibicao:
        endereco_cliente = clientes_exibicao[destino_id][0]
        mensagem = criar_msg_texto(remetente_id, destino_id, texto)
        socket_cliente.sendto(mensagem, endereco_cliente)
    else:
        print(f"Cliente {destino_id} não encontrado.")

# Função que cria a mensagem de OI
def criar_msg_oi(cliente_id, username):
    username = username[:20].encode() + b'\0'  # Garante que o username tenha no máximo 20 bytes e termina com \0
    tipo_msg = 0  # 0 = OI
    mensagem = struct.pack('!iiii20s', tipo_msg, cliente_id, 0, 0, username)
    return mensagem

# Função que cria a mensagem de texto
def criar_msg_texto(remetente_id, destino_id, texto):
    texto = texto[:140].encode() + b'\0'  # Garante que o texto tenha no máximo 140 bytes e termina com \0
    tipo_msg = 1  # 1 = MSG
    tamanho = len(texto)
    mensagem = struct.pack('!iiii', tipo_msg, remetente_id, destino_id, tamanho) + texto
    return mensagem

# Função que cria a mensagem de TCHAU
def criar_msg_tchau(cliente_id):
    tipo_msg = 2  # 2 = TCHAU
    mensagem = struct.pack('!iii', tipo_msg, cliente_id, 0)
    return mensagem

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
