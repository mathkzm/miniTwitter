import socket
import sys
import struct
import threading

# Função que cria a mensagem de texto.
def criar_msg_texto(remetente_id, destino_id, texto, username):
    texto = texto[:140] + '\0'  # Garante que o texto tenha no máximo 140 caracteres e termina com \0
    tamanho_texto = len(texto)
    username = username[:20] + '\0'  # Garante que o username tenha no máximo 20 caracteres e termina com \0
    tipo_msg = 1  # 1 = Mensagem de texto (exemplo)
    mensagem = struct.pack('!iiii20s140s', tipo_msg, remetente_id, destino_id, tamanho_texto, username.encode(), texto.encode())
    return mensagem

# Função que cria a mensagem de TCHAU.
def criar_msg_tchau(cliente_id, username):
    username = username[:20] + '\0'  # Garante que o username tenha no máximo 20 caracteres e termina com \0
    tipo_msg = 2  # 2 = TCHAU (exemplo)
    mensagem = struct.pack('!iiii20s', tipo_msg, cliente_id, 0, 0, username.encode())
    return mensagem

# Função que cria a mensagem de OI
def criar_msg_oi(cliente_id, username):
    username = username[:20] + '\0'  # Garante que o username tenha no máximo 20 caracteres e termina com \0
    tipo_msg = 0  # 0 = OI (exemplo)
    mensagem = struct.pack('!iiii20s', tipo_msg, cliente_id, 0, 0, username.encode())
    return mensagem

# Função para enviar mensagem
def enviar_msg(sock, servidor_ip, servidor_porta, cliente_id, username):
    while True:
        texto = input("Digite a mensagem (ou TCHAU para sair): ")
        if texto == "TCHAU":
            mensagem = criar_msg_tchau(cliente_id, username)
            sock.sendto(mensagem, (servidor_ip, servidor_porta))
            break
        else:
            destino_id = int(input("Digite o ID do destinatário (0 para enviar a todos): "))
            mensagem = criar_msg_texto(cliente_id, destino_id, texto, username)
            sock.sendto(mensagem, (servidor_ip, servidor_porta))

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

    # Recebe a mensagem OI de volta
    resposta, _ = sock.recvfrom(1024)
    print(f"Resposta do servidor: {resposta.decode()}")

    # Cria uma thread para enviar mensagens
    enviar_thread = threading.Thread(target=enviar_msg, args=(sock, servidor_ip, servidor_porta, cliente_id, username))
    enviar_thread.start()
    enviar_thread.join()

if __name__ == "__main__":
    main()
