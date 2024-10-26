#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import threading
from socket import *
import logging
import struct
from datetime import datetime

MAX_CLIENTES = 15  # Limite de clientes conectados
clientes_envios_conectados = 0
clientes_exibicao_conectados = 0
tempo_inicio = time.time()

##################################################################################################################################################################################################
##################################################################################################################################################################################################

# Configuração do logging para registrar em um arquivo
logging.basicConfig(
    filename="log_servidor.log",  # Arquivo onde os logs serão armazenados
    level=logging.INFO,           # Nível de log: INFO significa que logs informativos serão registrados
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato das mensagens de log
    datefmt="%Y-%m-%d %H:%M:%S"   # Formato da data e hora
)

# Dicionários para armazenar os clientes
clientes_exibicao = {}  # {id: (endereço, tipo)}
clientes_envio = {}     # {id: (endereço, tipo)}
servidor_inicio = time.time()  # Para calcular o tempo de atividade do servidor

# Função para criar a mensagem periódica com as informações do servidor
def criar_mensagem_periodica():
    # Calcula o tempo de execução em segundos
    tempo_ativo = int(time.time() - tempo_inicio)
    identidade = "ServidorCentral"
    num_clientes_exibicao = len(clientes_exibicao)
    num_clientes_envio = len(clientes_envio)

    # Montando a mensagem
    tipo_mensagem = 1  # Exemplo de tipo MSG
    id_remetente = 0   # ID do servidor
    id_destinatario = 0  # 0 para todos os clientes
    texto = f"Identidade: {identidade} | Clientes Exibição: {num_clientes_exibicao} | Clientes Envio: {num_clientes_envio} | Uptime: {tempo_ativo}s"
    nome_remetente = "Servidor"[:20].ljust(20, '\0')  # Preenche com '\0' até 20 caracteres
    tamanho_texto = len(texto)

    # Monta a mensagem em bytes
    mensagem = struct.pack('!IIII20s140s', tipo_mensagem, id_remetente, id_destinatario, tamanho_texto, nome_remetente.encode(), texto.encode())
    
    return mensagem

# Função para enviar a mensagem periodicamente
def enviar_mensagem_periodica():
    while True:
        mensagem = criar_mensagem_periodica()
        for endereco, _ in clientes_exibicao.values():
            socket_cliente.sendto(mensagem, endereco)
        time.sleep(60)  # Envia a cada 60 segundos

##################################################################################################################################################################################################
##################################################################################################################################################################################################

# Recebe as mensagens dos clientes e processa conforme o tipo.
def processar_cliente():
    
    while True:
        try:
            msg, end = socket_cliente.recvfrom(1024)
            print(f"Mensagem recebida do cliente {end}: {msg}")  # Exibe a mensagem bruta recebida
            # Não tente decodificar diretamente a mensagem aqui, passe para processar_msg
            processar_msg(msg, end)
        except UnicodeDecodeError as e:
            print(f"Erro de decodificação da mensagem recebida de {end}: {msg}")
            print(f"Detalhes do erro: {e}")
        except (ConnectionResetError, OSError):
            # Trata desconexões inesperadas
            cliente_id = get_cliente_id_by_endereco(end)
            if cliente_id:
                remover_cliente(cliente_id)
                
# Obtém o cliente ID pelo endereço (caso de desconexão inesperada)
def get_cliente_id_by_endereco(end):
    
    for cliente_id, cliente_info in {**clientes_exibicao, **clientes_envio}.items():
        if cliente_info[0] == end:
            return cliente_id
    return None

##################################################################################################################################################################################################
##################################################################################################################################################################################################

def processar_msg(msg, end):
    
    try:
        # Tente desempacotar os primeiros 16 bytes (quatro inteiros)
        tipo_msg, remetente_id, destino_id, tamanho = struct.unpack('!iiii', msg[:16])
        print(f"tipo_msg: {tipo_msg}, remetente_id: {remetente_id}, destino_id: {destino_id}, tamanho: {tamanho}")
        
        # Tente decodificar o nome do usuário (20 caracteres)
        nome_usuario = msg[16:36].decode().rstrip('\0')
        print(f"Nome do usuário: {nome_usuario}")
        
        # Se houver texto, decodifique o texto a partir do byte 36
        if tamanho > 0:
            texto = msg[36:36 + tamanho].decode().rstrip('\0')
        else:
            texto = ''
        print(f"Texto: {texto}")
        
        # Processamento baseado no tipo de mensagem
        if tipo_msg == 0:  # OI
            recebe_oi_cliente(remetente_id, end, nome_usuario)
        elif tipo_msg == 1:  # MSG
            enviar_msg(remetente_id, destino_id, texto, end, nome_usuario)
        elif tipo_msg == 2:  # TCHAU
            remover_cliente(remetente_id)
        # elif tipo_msg == 3:  # ERRO
        #    enviar_erro(remetente_id)
        elif tipo_msg == 4:  # LISTAR
            listar_clientes_ativos(socket_cliente, end)
    
    except struct.error as e:
        print(f"Erro ao processar a mensagem recebida de {end}: {msg}")
        print(f"Detalhes do erro: {e}")
    
##################################################################################################################################################################################################
##################################################################################################################################################################################################

def recebe_oi_cliente(remetente_id, endereco, nome_remetente):
    
    sucesso = registrar_cliente(remetente_id, endereco, nome_remetente)
    if sucesso:
        # Envia uma resposta de sucesso
        resposta = struct.pack("!iiii", 1, remetente_id, 0, 0)
        socket_cliente.sendto(resposta, endereco)

def enviar_msg(remetente_id, destino_id, texto, endereco=None, username=None):
    
    if destino_id == 0:  # Envia para todos os clientes de exibição
        for cliente in clientes_exibicao.values():
            endereco_cliente = cliente[0]
            mensagem = criar_msg_texto(remetente_id, 0, texto, username)
            socket_cliente.sendto(mensagem, endereco_cliente)
    elif destino_id in clientes_exibicao:
        endereco_cliente = clientes_exibicao[destino_id][0]
        mensagem = criar_msg_texto(remetente_id, destino_id, texto, username)
        socket_cliente.sendto(mensagem, endereco_cliente)
    elif destino_id in clientes_envio:
        print(f"Enviando mensagem para cliente de envio {destino_id}.")
        endereco_cliente = clientes_envio[destino_id][0]
        mensagem = criar_msg_texto(remetente_id, destino_id, texto, username)
        socket_cliente.sendto(mensagem, endereco_cliente)
    else:
        print(f"Cliente {destino_id} não encontrado.")
        
# Função que cria a mensagem de TCHAU
def criar_msg_tchau(remetente_id, endereco_servidor):
    # Cabeçalho: tipo (2 para TCHAU), id do remetente, id do destino (0 para TCHAU), tamanho do texto (0 para TCHAU)
    tipo = 2
    destino_id = 0
    tamanho_texto = 0
    msg_tchau = struct.pack('!iiii', tipo, remetente_id, destino_id, tamanho_texto) + b'\0' * 161

    # Envia a mensagem de TCHAU ao servidor
    socket_cliente.sendto(msg_tchau, endereco_servidor)
    print(f"Mensagem TCHAU enviada para o servidor pelo cliente {remetente_id}.")

    # Remove o cliente chamando a função remover_cliente
    remover_cliente(remetente_id)
            
def enviar_erro(endereco, mensagem_erro):

    tipo_msg = 3
    remetente_id = 0
    destinatario_id = 0
    texto_erro = mensagem_erro.encode().ljust(140, b'\0')
    mensagem = struct.pack("!iiii140s", tipo_msg, remetente_id, destinatario_id, len(texto_erro), texto_erro)
    socket_cliente.sendto(mensagem, endereco)
    
def listar_clientes_ativos(socket_cliente, end):
    
    if not clientes_exibicao:
        socket_cliente.sendto("Nenhum cliente exibidor ativo.".encode(), end)
        return

    lista_clientes = "Clientes exibidores ativos:\n"
    for client_id, (client_end, username) in clientes_exibicao.items():
        lista_clientes += f"ID: {client_id}, Usuário: {username}\n"

    socket_cliente.sendto(lista_clientes.encode(), end)
    logging.info(f"Lista de clientes ativos enviada para {end}.")    

##################################################################################################################################################################################################
##################################################################################################################################################################################################

# Registra o cliente (envio ou exibição) e faz log da entrada.
def registrar_cliente(remetente_id, end, username):
    
    global clientes_exibicao_conectados, clientes_envios_conectados

    # Verifica se o cliente é do tipo exibição (ID entre 1 e 999)
    if 1 <= remetente_id <= 999:
        if remetente_id in clientes_exibicao:
            enviar_erro(end,"ERRO {remetente_id} ID já em uso por outro cliente exibidor")
            logging.error(f"Tentativa de registro com ID já em uso: {remetente_id}")
            return False

        if (remetente_id + 1000) in clientes_envio:
            enviar_erro(end, "ERRO {remetente_id} ID de exibição conflitante com cliente de envio")
            logging.error(f"Tentativa de registro com ID exibidor conflitante: {remetente_id + 1000}")
            return False

        # Adiciona cliente de exibição
        clientes_exibicao[remetente_id] = (end, username)
        clientes_exibicao_conectados += 1
        logging.info(f"Cliente exibidor {username} (ID {remetente_id}) registrado com sucesso.")
        return True

    # Verifica se o cliente é do tipo envio (ID entre 1001 e 1999)
    elif 1001 <= remetente_id <= 1999:
        if remetente_id in clientes_envio:
            enviar_erro(end, "ERRO {remetente_id} ID já em uso por outro cliente de envio")
            logging.error(f"Tentativa de registro com ID já em uso: {remetente_id}")
            return False

        if (remetente_id - 1000) in clientes_exibicao:
            enviar_erro(end, "ERRO {remetente_id} ID de envio conflitante com cliente de exibição")
            logging.error(f"Tentativa de registro com ID de envio conflitante: {remetente_id - 1000}")
            return False

        # Adiciona cliente de envio
        clientes_envio[remetente_id] = (end, username)
        clientes_envios_conectados += 1
        logging.info(f"Cliente de envio {username} (ID {remetente_id}) registrado com sucesso.")
        return True

    else:
        enviar_erro(end, "ERRO {remetente_id} Identificador inválido")
        logging.error(f"Tentativa de registro com ID inválido: {remetente_id}")
        return False
    
# Remove o cliente da lista de exibidores ou de envio, faz log da saída.
def remover_cliente(remetente_id):
    
    global clientes_exibicao_conectados, clientes_envios_conectados

    if remetente_id in clientes_exibicao:
        username = clientes_exibicao[remetente_id][1]
        del clientes_exibicao[remetente_id]
        clientes_exibicao_conectados -= 1  # Atualiza o contador de clientes de exibição
        logging.info(f"Cliente {username} (ID {remetente_id}) saiu do sistema.")
    elif remetente_id in clientes_envio:
        username = clientes_envio[remetente_id][1]
        del clientes_envio[remetente_id]
        clientes_envios_conectados -= 1  # Atualiza o contador de clientes de envio
        logging.info(f"Cliente {username} (ID {remetente_id}) saiu do sistema.")
    else:
        logging.warning(f"Tentativa de remover cliente com ID desconhecido: {remetente_id}")

# Função que cria a mensagem de texto        
def criar_msg_texto(remetente_id, destino_id, texto, username):
    
    if username is None:
        username = ''

    # Calcula o tamanho do texto
    tamanho_texto = len(texto)

    # Cria a mensagem usando struct
    mensagem = struct.pack(
        '!IIII20s140s',  # Formato da mensagem
        1,  # Tipo de mensagem
        remetente_id,  # ID do remetente
        destino_id,  # ID do destinatário
        tamanho_texto,  # Passar o tamanho do texto aqui
        username.encode().ljust(20, b'\0'),  # Nome do usuário, preenchido com bytes nulos
        texto.encode().ljust(140, b'\0')  # Texto da mensagem, preenchido com bytes nulos
    )
    return mensagem
##################################################################################################################################################################################################
##################################################################################################################################################################################################
    
# Função principal para configurar o servidor e iniciar a comunicação
def main():
    global socket_cliente
    socket_cliente = socket(AF_INET, SOCK_DGRAM)
    socket_cliente.bind(('localhost', 12345))

    print("Servidor iniciado e aguardando mensagens...")

    # Cria uma thread para envio de mensagens periódicas
    threading.Thread(target=enviar_mensagem_periodica, daemon=True).start()

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
