import datetime
import numpy as np

numeroErrosE = 0
numeroErrosF = 0
contadorMensagens = 0
totalMensagens = 1e6

def escuto(probErroE=0.1, probErroF=0.1):
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

def simulacao(totalMensagens=1e6, probErroE=0.1, probErroF=0.1, esperar=False, imprime=False):
	contadorMensagens = 0
	while True and contadorMensagens < totalMensagens:			
		# escuto
		estadoDaComunicacao = escuto(probErroE=probErroE, probErroF=probErroF)
		# se silêncio -> transmite
		if estadoDaComunicacao == "silencio":
			if imprime:
				print(f"mensagem {contadorMensagens} de dado enviada")
		# se não -> espera
		else:
			if imprime:
				print(f"mensagem {contadorMensagens} de dado não enviada")
			if esperar:
				espera()
			continue

		# escuto
		estadoDaComunicacao = escuto(probErroE=probErroE, probErroF=probErroF)
		# se ok -> transmite controle
		if estadoDaComunicacao == "silencio":
			if imprime:
				print(f"mensagem {contadorMensagens} de controle recebida")
			contadorMensagens += 1
			continue
		# se não -> espera e tenta novamente mesma mensagem
		else:
			if imprime:
				print(f"mensagem {contadorMensagens} de controle não recebida")
			if esperar:
				espera()
			continue

	return numeroErrosE, numeroErrosF

if __name__ == "__main__":
	totalMensagens = 1e3 # total de mensagens a serem transmitidas
	probsErroE = [0.2] # probabilidade de mensagem ser corrompida
	probsErroF = [0.2] # probabilidade de mensagem ser perdida
	
	numeroErrosE_ = []
	numeroErrosF_ = []

	for i in range(len(probsErroE)):
		numeroErrosE, numeroErrosF = simulacao(totalMensagens, probsErroE[i], probsErroF[i])
		numeroErrosE_.append(numeroErrosE)
		numeroErrosF_.append(numeroErrosF)

	print(f"numero de erros E: {numeroErrosE_}")
	print(f"numero de erros F: {numeroErrosF_}")