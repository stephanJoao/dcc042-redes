import datetime
import numpy as np

# percErr1 = np.random.randint(2,10)
# percErr2 = np.random.randint(2,10)
# def escuto():
#     e = np.random.randint(1,percErr1)
#     f = np.random.randint(1,percErr2)
#     print(e)
#     print(f)
#     erroE = np.random.randint(0,30, size=(e)) 
#     erroF = np.random.randint(0,30, size=(f)) 
#     probabilidadeTotal = np.arange(0,30,1)
#     np.random.shuffle(probabilidadeTotal)
#     escolhedor = np.random.randint(0,30)
#     print(escolhedor)
#     print(erroE)
#     print(erroF)
#     valor = probabilidadeTotal[escolhedor]
#     if valor in erroE:
#         return "erroE"
#     elif valor in erroF:
#         return "erroF"
#     else:
#         return "silencio"

valorErroE = 0.2
valorErroF = 0.2

numeroErrosE = 0
numeroErrosF = 0
def escuto():
    rand = np.random.uniform()
    if rand < valorErroE:
        numeroErrosE +=1 
        return "erroE"
    elif rand > valorErroE and rand < valorErroF + valorErroE:
        numeroErrosF +=1
        return "erroF"
    else:
        return "silencio"

def contatempo():
    start_time = datetime.datetime.now()
    print(start_time)
    count = 0 
    while True and count <3:
        if (datetime.datetime.now() - start_time).seconds == 1:
            start_time = datetime.datetime.now()
            print(start_time)
            count += 1

mensagemEnviada = False
mensagemRecebida = True
contador = 0
while True:
    
    estadoDaComunicacao = escuto()
    if estadoDaComunicacao == "silencio":
        print(f"mensagem {contador} de dado enviada")
        mensagemEnviada = True
    else:
        mensagemEnviada = False
        contatempo()
        continue

    estadoDaComunicacao = escuto()

    if estadoDaComunicacao == "silencio" and mensagemEnviada:
        print(f"mensagem {contador} de controle enviada")
        mensagemRecebida = True
    else:
        mensagemRecebida = False
        print("mensagem não recebida")
        contatempo()
        continue

    if mensagemRecebida:
        contador += 1
    
    