###	INTEGRANTES DO GRUPO ###
# Ana Beatriz Lana Maciel Moreira Armond - 202165501B
# Gabriel Maciel Furlong - 201965204AB
# João Stephan Silva Maurício - 201965505b
# Hiero Henrique Barcelos Costa - 202065136B
# Arthur Malvacini Franchesqueti - 201865503B


import datetime
import numpy as np
import matplotlib.pyplot as plt

def plota3D(a, b, funcao):
	fig = plt.figure(figsize=(16, 8))
	ax1 = fig.add_subplot(121, projection='3d')
	ax2 = fig.add_subplot(122, projection='3d')

	_xx, _yy = np.meshgrid(a, b)
	x, y = _xx.ravel(), _yy.ravel()

	top1 = []
	top2 = []
	for j in range(len(x)):
		top1.append(funcao(x[j], y[j])[0])
		top2.append(funcao(x[j], y[j])[1])
	top1 = np.array(top1)
	top2 = np.array(top2)
	print(top1)
	print(top2)

	bottom = np.zeros_like(top1)
	width = depth = 0.05

	ax1.bar3d(x, y, bottom, width, depth, top1, shade=True, color='#d17a00')
	ax1.set_title('Erro E')
	ax1.set_xlabel("Prob. erro E")
	ax1.set_ylabel("Prob. erro F")
	ax1.set_zlabel("Número de erros")

	ax2.bar3d(x, y, bottom, width, depth, top2, shade=True, color='#0489B1')
	ax2.set_title('Erro F')
	ax2.set_xlabel("Prob. erro E")
	ax2.set_ylabel("Prob. erro F")
	ax2.set_zlabel("Número de erros")

	plt.savefig('myfile.png', bbox_inches="tight")
	plt.show()

def escuto(probErroE, probErroF, numeroErrosE, numeroErrosF):
	rand = np.random.uniform()
	if rand < probErroE:
		return "erroE"
	elif rand > probErroE and rand < probErroF + probErroE:
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

def simulacao(probErroE=0.1, probErroF=0.1, totalMensagens=1e3, esperar=False, imprime=False):
	contadorMensagens = 0
	numeroErrosE = 0
	numeroErrosF = 0
	while True and contadorMensagens < totalMensagens:
		# escuto
		estadoDaComunicacao = escuto(probErroE, probErroF, numeroErrosE, numeroErrosF)
		# Soma Erros
		if estadoDaComunicacao == "erroE":
			numeroErrosE+=1
		elif estadoDaComunicacao == "erroF":
			numeroErrosF+=1
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
		estadoDaComunicacao = escuto(probErroE, probErroF, numeroErrosE, numeroErrosF)
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
	probsErroE = np.arange(0.05, 0.50, 0.05) # probabilidade de mensagem ser corrompida
	probsErroF = np.arange(0.05, 0.50, 0.05) # probabilidade de mensagem ser perdida

	plota3D(probsErroE, probsErroF, simulacao)
	smkl

	numeroErrosE_ = []
	numeroErrosF_ = []

	for i in range(len(probsErroE)):
		numeroErrosE, numeroErrosF = simulacao(totalMensagens, probsErroE[i], probsErroF[i])
		numeroErrosE_.append(numeroErrosE)
		numeroErrosF_.append(numeroErrosF)

	print(f"numero de erros E: {numeroErrosE_}")
	print(f"numero de erros F: {numeroErrosF_}")

	# plotagem
	plt.plot(probsErroE, numeroErrosE_, label="Erros E")
	plt.plot(probsErroF, numeroErrosF_, label="Erros F")
	plt.xlabel("Probabilidade de erro")
	plt.ylabel("Número de erros")
	plt.legend()
	plt.grid()
	plt.show()