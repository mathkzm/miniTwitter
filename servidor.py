import time
import signal
import threading
from socket import *

# Dicionário para armazenar os clientes de exibição (id: (endereço, tipo))
clientes_exibicao = {}

# Dicionário para armazenar os clientes de envio (id: (endereço, tipo))
clientes_envio = {}

# Envia a mensagem identidade periódica.
def envio_msg_periodica(signum, frame):
    mensagem_identidade = criar_msg_identidade()
    for cliente in clientes_exibicao.values():
        endereco = cliente[0]
        enviar_msg(0, endereco, mensagem_identidade)

# Retorna uma mensagem dizendo o número de clientes de envio e de exibição conectados ao servidor.
def criar_msg_identidade():
    num_envio = len(clientes_envio)
    num_exibicao = len(clientes_exibicao)
    tempo_ativo = time.strftime("%H:%M:%S", time.gmtime(time.time()))
    return f"Identidade: {num_envio} clientes de envio, {num_exibicao} clientes de exibição. Servidor ativo há {tempo_ativo}."


# Recebe a mensagem, divide entre mensagem e endereço e chama a função para processar a mensagem.
def processar_cliente(socket_cliente):
    while True:
        try:
            msg, end = socket_cliente.recvfrom(1024)
            processar_msg(msg.decode(), end)
        except ConnectionResetError:
            break

# Decodifica a mensagem entre tipo, endereço do remetente, endereço do destinatário e o texto, de acordo com
# as especificações do trabalho.
def processar_msg(msg, end):
    partes = msg.split(" ")
    tipo = partes[0]
    remetente_id = int(partes[1])
    destino_id = int(partes[2])
    texto = " ".join(partes[3:])
    
    if tipo == "MSG":
        enviar_msg(remetente_id, destino_id, texto)
    elif tipo == "OI":
        registrar_cliente(remetente_id, end)
    elif tipo == "TCHAU":
        remover_cliente(remetente_id)

# Verifica se o cliente já está cadastrado como de envio ou de exibição, caso não esteja, de acordo com os endereços
# especificados no trabalho, registra como de envio ou de exibição.
def registrar_cliente(cliente_id, end):
    if cliente_id % 2 == 0:  # Exemplo de separação por ID par/ímpar
        clientes_exibicao[cliente_id] = (end, 'exibicao')
    else:
        clientes_envio[cliente_id] = (end, 'envio')

# Deleta o cliente da lista de clientes de exibição ou de envio. Verificar na especificação do trabalho se precisa
# usar a lógica da mensagem TCHAU nessa situação.
def remover_cliente(cliente_id):
    if cliente_id in clientes_exibicao:
        del clientes_exibicao[cliente_id]
    elif cliente_id in clientes_envio:
        del clientes_envio[cliente_id]

# Função para enviar a mensagem. Verifica se o remetente é válido. Se for 0, a msg deve ser enviada a todos os usuários
# Se não for 0, envia apenas para o destinatário especifico.
def enviar_msg(remetente_id, destino_id, texto):
    if destino_id == 0:  # Envia para todos
        for cliente in clientes_exibicao.values():
            endereco = cliente[0]
            socket_cliente.sendto(f"MSG {remetente_id} {destino_id} {texto}".encode(), endereco)
    elif destino_id in clientes_exibicao:
        endereco = clientes_exibicao[destino_id][0]
        socket_cliente.sendto(f"MSG {remetente_id} {destino_id} {texto}".encode(), endereco)


# Configura o socket
# Configura o sinal para o envio de mensagens periódicas
# Inicia a thread para processar os clientes.
def main():
    global socket_cliente
    socket_cliente = socket(AF_INET, SOCK_DGRAM)
    socket_cliente.bind(('localhost', 12345))

    # Configura o sinal para envio de mensagens periódicas
    signal.signal(signal.SIGALRM, envio_msg_periodica)
    signal.setitimer(signal.ITIMER_REAL, 60, 60)  # A cada minuto

    # Cria uma thread para processar novos clientes
    threading.Thread(target=processar_cliente, args=(socket_cliente,)).start()

    print("Servidor iniciado e aguardando mensagens...")

if __name__ == "__main__":
    main()



# Explicação do código:
# envio_msg_periodica: Envia uma mensagem com a "identidade" do servidor (número de clientes conectados e tempo ativo) a cada minuto para todos os clientes de exibição.

# criar_msg_identidade: Gera a mensagem de identidade, que será enviada periodicamente.

# processar_cliente: Recebe e processa mensagens de clientes continuamente em uma thread separada.

# processar_msg: Processa cada mensagem recebida, identificando se é uma mensagem normal (MSG), uma solicitação de registro (OI), ou uma desconexão (TCHAU).

# registrar_cliente: Registra clientes como de envio ou exibição com base no identificador.

# remover_cliente: Remove clientes que enviam a mensagem TCHAU ou desconectam.

# enviar_msg: Envia a mensagem para todos os clientes ou para um destinatário específico.

# main: Configura o servidor de socket, define o temporizador para o envio das mensagens periódicas e inicia o processamento dos clientes em uma thread.
