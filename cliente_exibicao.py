import socket
import sys
import struct
import threading

# Função que cria a mensagem de OI
def criar_msg_oi(id_cliente, nome_usuario):
    tipo = 0  # Tipo de mensagem OI
    destino_id = 0  # ID do destinatário
    tamanho_texto = len(nome_usuario)  # Tamanho do texto
    # Criação da mensagem, ajustando o preenchimento para 20 e 140 bytes
    return struct.pack('!iiii', tipo, id_cliente, destino_id, tamanho_texto) + nome_usuario.encode().ljust(20, b'\0') + b'\0' * 141

def main():
    if len(sys.argv) != 4:
        print("Uso correto: python cliente_exibicao.py <ID> <nome_usuario> <endereço_servidor:porta>")
        sys.exit(1)
    
    id_cliente = int(sys.argv[1])
    nome_usuario = sys.argv[2]
    end_servidor = sys.argv[3].split(":")
    ip_servidor = end_servidor[0]
    porta_servidor = int(end_servidor[1])

    sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    msg_oi = criar_msg_oi(id_cliente, nome_usuario)
    sockUDP.sendto(msg_oi, (ip_servidor, porta_servidor))

    print("Solicitação de conexão inicial enviada ao servidor.")

    # Processar resposta do servidor
    try:
        resposta, _ = sockUDP.recvfrom(176)  # Espera pela resposta correta
        print(f"Resposta recebida do servidor: {resposta}")

        tipo_resposta, remetente_id, destino_id, tamanho_texto = struct.unpack('!iiii', resposta[:16])
        nome_usuario = resposta[16:36].decode().strip('\x00')  # Nome do usuário
        texto = resposta[36:176].decode().strip('\x00')  # Texto 

        print(f"Tipo de resposta: {tipo_resposta}, Remetente ID: {remetente_id}, Nome do usuário: {nome_usuario}, Texto: {texto}")

        if tipo_resposta == 0:  # Resposta de OI
            print(f"Cliente de exibição {remetente_id} registrado com sucesso no servidor.")
            
            # Inicia thread para receber mensagens do servidor
            threading.Thread(target=receber_msgs, args=(sockUDP,), daemon=True).start()

            # Mantendo o cliente em execução
            while True:
                pass
        elif tipo_resposta == 1:
                print("recebi mensagem")

        elif tipo_resposta == 3:  # Resposta de erro
            erro_texto = texto
            print(f"Erro recebido do servidor: {erro_texto}")
            print("Encerrando o programa devido ao erro.")
            sys.exit(1)
        
        elif tipo_resposta == 4:  # Resposta de LISTAR
            lista_cliente_envio_online = texto
            print(f"Clientes de envio conectados: {lista_cliente_envio_online}")

        else:
            print(f"Erro: resposta inesperada do servidor. Tipo: {tipo_resposta}")
            sys.exit(1)

    except struct.error as e:
        print(f"Erro ao processar a resposta do servidor: {e}")
        print("Possível causa: o tamanho da mensagem recebida não é o esperado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado ao processar a resposta do servidor: {e}")
        sys.exit(1)

# Função para receber mensagens do servidor
def receber_msgs(sock):
    while True:
        try:
            resposta, _ = sock.recvfrom(176)  # Espera exatamente 176 bytes
            print(f"Resposta recebida do servidor: {resposta}")

            # Processa a resposta
            tipo_resposta, remetente_id, destino_id, tamanho_texto = struct.unpack('!iiii', resposta[:16])
            nome_usuario = resposta[16:36].decode().strip('\x00')
            texto = resposta[36:176].decode().strip('\x00')

            print(f"Nome do usuário: {nome_usuario}")
            print(f"Texto recebido: {texto}")

        except struct.error as e:
            print(f"Erro ao desempacotar a resposta: {e}")
            print("Erro: formato de resposta inesperado.")
        except Exception as e:
            print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()
