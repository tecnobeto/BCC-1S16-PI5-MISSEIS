# importando todas as bibliotecas necessárias
import asyncio # Para métodos que rodam assincronamente
import websockets # Cuida dos métodos de websocket
import time 
from base import Base
from aviao import Aviao
from bala import Bala

import threading
import math
import os

# import shlex

# Inicializa base no centro
base = Base(5000, 5000, 0) 
aviao = Aviao(0, 0, 0)
bala = Bala(base, 0, 0)

print("tipo: " + str(aviao.tipo))
distancia = 1000000000
jaEnviouParaClient = 0


# Classe Servidor - Cuida das funções do servidor - é a base
class Servidor:
    def __init__(self):
        self.tempos = []
    
    
    # Colocando esse codigo antes, executamos a função em modo assincrono
    @asyncio.coroutine
    def conecta(self, websocket, path): 
        cliente = Cliente(self, websocket, path)

        print("Radar conectado.\n")
        yield from cliente.gerencia() # Com o yield podemos garantir que será executado de forma sequencial, colocando em uma fila.

    # Função para desconectar o cliente que entrou no servidor.
    def desconecta(self, cliente):
        print("Radar desconectado.")     


# Classe Cliente - Cuida das funçoes de transferencia de mensagem
class Cliente:  
    # Inicializa a classe do websocket  
    def __init__(self, servidor, websocket, path):
        self.cliente = websocket
        self.servidor = servidor

    # De forma assincrona, gerencia as conexões dos usuários no websocket
    @asyncio.coroutine
    def gerencia(self):
        try:
            # De forma sequencial, envia a todos os usuários a mensagem
            yield from self.envia("Radar Conectado")


            while True: # Enquanto a mensagem não chegar o servidor fica esperando
                # Escreve a mensagem vinda do teclado
                #mensagem = input("Digite sua mensagem: ") # Pode digitar qualquer mensagem diferente de vazio
                
                #Coloca o tempo na hora de enviar a mensagem e envia
                tempoEnvio = time.time()
                tempoTotal = 0;
                intervaloLimite = 2;

                mensagemTotal = ""#mensagem
                result = "1";

                #print("\nEnviando....")

                while result == "1" and tempoTotal < intervaloLimite:
                    #print(distancia)
                    if distancia <= 3000:
                        global jaEnviouParaClient
                        global bala

                        if jaEnviouParaClient == 0:
                            mensagemTotal = str(aviao.x) + ";" + str(aviao.y) + ";" + str(aviao.z) + ";" + str(aviao.vx) + ";" + str(aviao.vy) + ";" + str(tempoEnvio)

                            yield from self.envia(mensagemTotal)
                    
                            # Recebe o retorno e pega o tempo que demora para ele retornar
                            result = yield from self.recebe()

                            arrayResult = result.split(";")
                            anguloAzimute = float(arrayResult[0])
                            angulo = float(arrayResult[1])

                            bala = Bala(base, anguloAzimute, angulo)

                            bala.atualizaVelocidades()
                            # print(bala.anguloAzimute)
                            # print(bala.x)
                            # print(bala.angulo)


                            tempoRecebimento = time.time()
                            tempoTotal = tempoRecebimento - tempoEnvio
                            
                           
                            jaEnviouParaClient = 1

                    else:
                        result = 0
                    #     mensagemTotal = "y"
                        
                    # yield from self.envia(mensagemTotal)
                
                    # # Recebe o retorno e pega o tempo que demora para ele retornar
                    # result = yield from self.recebe()

                    
                    # tempoRecebimento = time.time()
                    # tempoTotal = tempoRecebimento - tempoEnvio
                    
                    # # Aqui ele pega os dados necessários para o tiro no canhão
                    # # Será processado abaixo
                    # arrayResult = result.split(";")
                    
                    # # Aqui estão as coordenadas do avião
                    # angulacao = arrayResult[0]
                    # outrasInfo = arrayResult[1]
                    
                    
                    #print(arrayResult)

                    # Coloquei -1002, pois 1 km da base pra ser considerado acerto e 2 metros de raio do avião 
                    # distancia = base.distanciaEuclidiana(arrayResultNum) - 1002
                    
                    # Se ele chgar a uma distancia de 3 km e for desistir
                    '''
                    if (distancia < 3000 and vaiDesistir == 1):
                        # volta para uma altitude de 1200 m e velocidade de 750km/h ou 208,333 m/s
                        yield from self.envia("a")
                        # lá no client trata se ele já foi enviado uma vez a atualizacao
                        
                    elif distancia <= 0:
                        print("-----------------BASE ATINGIDA----------------")
                        yield from self.envia("d") # Destruida = d = base destruida
                        
                        
                    # Se a distancia for menor que 10km pode atirar de acordo que o mario 
                    # ache que é o momento certo, coloque as validações aqui
                    if distancia < 10000:
                        # dentro da classe base tem 4 balas com funcoes que ajudam
                        print("menos que 10 km")
                        #print(str(balaAtual.x) + ";" + str(balaAtual.y) + ";" + str(balaAtual.z))
                    
                        
                    print("Distancia entre avião: " + str(distancia))
                    '''


                # Está fora do while
                if result == "1":
                    print("Falha no envio, tempo limite excedido.")
                else:
                    servidor.tempos.append(tempoTotal);
                    #print("Enviado! (tempo total: {0})".format(tempoTotal))
                    total = 0
                    for tempo in servidor.tempos:
                        total += tempo

                    #print("tempo medio: {0}".format(total / len(servidor.tempos)) + "\n")
                    
        except Exception:
            print("Erro")
            raise        
        finally:
            self.servidor.desconecta(self)

    # Envia mensagem pelo websocket
    @asyncio.coroutine
    def envia(self, mensagem):
        yield from self.cliente.send(mensagem)

    # Recebe mensagem via websocket
    @asyncio.coroutine
    def recebe(self):
        mensagem = yield from self.cliente.recv()
        return mensagem
    
# Esta função atualiza o avião
def atualizaPosicaoAviao():
    t = threading.Timer(0.03, atualizaPosicaoAviao).start()
    
    # print("BASE - x = " + str(base.x) + "; y = " + str(base.y) + "; z = " + str(base.z))
    # print("BASE - x = {:5.2f}; y = {:5.2f}; z = ".format(base.x, base.y) + str(base.z))
    # print("AVIAO - x = " + str(aviao.x) + "; y = " + str(aviao.y) + "; z = " + str(aviao.z))
    print("AVIAO - x = {:5.2f}; y = {:5.2f}; z = ".format(aviao.x, aviao.y) + str(aviao.z))
    # print("TEMPO VOANDO - " + str(aviao.tempoVoando) + "s")
    verificaDistanciaBaseAviao()
    aviao.atualizaPosicao()
    bala.atualizaPosicao()
    
# Verifica a distancia entre a base e o avião
def verificaDistanciaBaseAviao():
    distX = base.x - aviao.x
    distY = base.y - aviao.y
    distZ = 0 - aviao.z

    global distancia

    distancia = math.sqrt(distX * distX + distY * distY + distZ * distZ)
    print("DISTANCIA - {:5.2f}m\n".format(distancia))
    
    # Verifica se acertou o alvo
    if distancia < 1000: # Base tem 1000 de raio
        print("Acertou o alvo")                    
        reiniciaAviao()


    # Verifica se está no intervalo de desistencia
    if distancia <= 3000:
        aviao.verificaDesistencia()
        mensagemTotal = "x"


    if distancia > 5000 and aviao.tempoVoando > 1:
        print("Avião Saiu do Raio")
        reiniciaAviao()


def reiniciaAviao():
    print("'s' - Se quiser sair do programa")
    print("'a' - Se quiser criar um aviao")

    op = input("")

    if op == 's':
        print("Programa foi fechado")
        os._exit(1)

    elif op == 'a':
        print("Avião foi criado")
        aviao.reiniciaAviao()



# O que precisa fazer?
# - Calcular a distancia de 3000 m
# - Calcular a distancia de 1000 m
# - Calcular se colidiu mesmo
    
# Criando o servidor efetivamente
servidor = Servidor()
loop = asyncio.get_event_loop()

# Inicializa o servidor com web socket 
start_server = websockets.serve(servidor.conecta, '0.0.0.0', 10769) # Usa-se 0.0.0.0 para pegar o ip do computador local

# Usa um trycatch para deixar rodando infinitamente o servidor de websocket
try:
    reiniciaAviao()
    atualizaPosicaoAviao()
    print("Servidor iniciado!")
    print("Esperando conexão de cliente...")
    loop.run_until_complete(start_server)
    loop.run_forever()
#    t.start()
except(KeyboardInterrupt, SystemExit):
        start_server.close()
        loop.stop()
        sys.exit(0)
        websockets.close()

finally:
    start_server.close()
 