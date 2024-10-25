#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
import threading
import struct

# Função que cria a mensagem de OI
def criar_msg_oi(cliente_id, username):
    username = username[:20].ljust(20, '\0')  # Preenche até 20 caracteres
    tipo_msg = 0  # OI
    tamanho = 0  # Nenhum texto extra na mensagem OI
    mensagem = struct.pack('!iiii20s', tipo_msg, cliente_id, 0, tamanho, username.encode('utf-8'))
    return mensagem

# Função que cria a mensagem de texto
def criar_msg_texto(remetente_id, destino_id, texto, username):
    tipo_msg = 1  # Tipo da mensagem para texto
    tamanho_texto = len(texto)

    # Prepara o nome do usuário
    nome_usuario = username.encode()[:20]  # Limita a 20 bytes
    nome_usuario += b'\x00' * (20 - len(nome_usuario))  # Preenche com \0 se necessário

    # Prepara o texto da mensagem
    texto_bytes = texto.encode()[:140]  # Limita a 140 bytes
    texto_bytes += b'\x00' * (140 - len(texto_bytes))  # Preenche com \0 se necessário

    # Empacota a mensagem
    mensagem = struct.pack('!iiii20s140s', tipo_msg, remetente_id, destino_id, tamanho_texto, nome_usuario, texto_bytes)
    return mensagem

# Função que cria a mensagem TCHAU
def criar_msg_tchau(cliente_id):
    tipo_msg = 2  # TCHAU
    destino_id = 0  # Destinatário indefinido para TCHAU
    tamanho_texto = 0  # Sem texto no TCHAU
    mensagem = struct.pack('!iiii', tipo_msg, cliente_id, destino_id, tamanho_texto) + b'\0' * 161
    return mensagem

# Função para enviar mensagens
def enviar_msg(sock, servidor_ip, servidor_porta, cliente_id, username):
    while True:
        texto = input("Digite a mensagem (ou TCHAU para sair): ")
        if texto.strip().upper() == "TCHAU":
            mensagem_tchau = criar_msg_tchau(cliente_id)
            sock.sendto(mensagem_tchau, (servidor_ip, servidor_porta))
            print("Mensagem TCHAU enviada.")
            break
        try:
            destino_id = int(input("Digite o ID do destinatário (0 para enviar a todos): "))
            mensagem = criar_msg_texto(cliente_id, destino_id, texto, username)  # Adicione o username aqui
            sock.sendto(mensagem, (servidor_ip, servidor_porta))
        except ValueError:
            print("ID do destinatário deve ser um número.")

# Função principal
def main():
    if len(sys.argv) != 4:
        print("Uso: python cliente_envio.py <ID> <nome_usuario> <endereço_servidor:porta>")
        sys.exit(1)

    cliente_id = int(sys.argv[1])
    username = sys.argv[2]
    servidor_info = sys.argv[3].split(":")
    servidor_ip = servidor_info[0]
    servidor_porta = int(servidor_info[1])

    # Inicializa o socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Envia a mensagem OI na inicialização
    mensagem_oi = criar_msg_oi(cliente_id, username)
    sock.sendto(mensagem_oi, (servidor_ip, servidor_porta))

    # Recebe resposta do servidor
    try:
        resposta, _ = sock.recvfrom(1024)
        print(f"Resposta recebida do servidor: {resposta}")

        # Verifica o tamanho da resposta para determinar o processamento
        if len(resposta) >= 16:
            tipo_resposta, remetente_id, destino_id, tamanho_texto = struct.unpack('!iiii', resposta[:16])

            # Tratamento para resposta de OI
            if tipo_resposta == 1 and tamanho_texto == 0:
                print("Conexão estabelecida com sucesso com o servidor. OI recebido.")
                
                # Cria uma thread para enviar mensagens
                enviar_thread = threading.Thread(target=enviar_msg, args=(sock, servidor_ip, servidor_porta, cliente_id, username))
                enviar_thread.start()
                enviar_thread.join()
            
            # Tratamento para resposta de ERRO
            elif tipo_resposta == 3:  # Assumindo que o tipo 3 indica uma mensagem de erro
                erro_texto = resposta[16:].decode(errors='ignore').strip('\x00')
                print(f"Erro recebido do servidor: {erro_texto}")
                sys.exit(1)
            
            else:
                print("Erro: formato de resposta inesperado.")
                sys.exit(1)

        else:
            print("Erro: resposta do servidor muito curta.")
            sys.exit(1)

    except socket.timeout:
        print("Erro: Tempo limite atingido para a resposta do servidor.")
        sys.exit(1)
    
        
if __name__ == "__main__":
    main()
