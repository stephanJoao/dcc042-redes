import datetime
import numpy as np

probErroE = 0.2 # probabilidade de mensagem ser corrompida
probErroF = 0.2 # probabilidade de mensagem ser perdida

numeroErrosE = 0
numeroErrosF = 0
contadorMensagens = 0

def escuto():
	global numeroErrosE, numeroErrosF
	rand = np.random.uniform()
	if rand < probErroE:
		numeroErrosE += 1 
		return "erroE"
	elif rand > probErroE and rand < probErroF + probErroE:
		numeroErrosF += 1
		return "erroF"
	else:
		return "silencio"

def espera():
	tempo = np.random.uniform(1, 3)
	print(f"esperando {tempo} segundos")
	inicio = datetime.datetime.now()
	while True:
		if (datetime.datetime.now() - inicio).total_seconds() > tempo:
			break

while True:			
	# escuto
	estadoDaComunicacao = escuto()
	# se silêncio -> transmite
	if estadoDaComunicacao == "silencio":
		print(f"mensagem {contadorMensagens} de dado enviada")
	# se não -> espera
	else:
		print(f"mensagem {contadorMensagens} de dados não recebida")
		espera()
		continue

	# escuto
	estadoDaComunicacao = escuto()
	# se ok -> transmite controle
	if estadoDaComunicacao == "silencio":
		print(f"mensagem {contadorMensagens} de controle recebida")
		contadorMensagens += 1
		continue
	# se não -> espera e tenta novamente mesma mensagem
	else:
		print(f"mensagem {contadorMensagens} de controle não recebida")
		espera()
		continue