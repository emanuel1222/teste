#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  servidor.py
#  

'''  
 * TRABALHO 1 - DISCIPLINA: REDES DE COMPUTADORES 2019/1
 * Programação Socket
 * Professor: Gilmar Vassoler - REDES
 * Alunos: Emanoel e Maikysuel
 '''
 
import socket
import struct
import _thread as thread
from random import randint
import time
from datetime import datetime, timedelta

HOST = '' #Endereco IP do Servidor
PORT = 5000 #Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria socket
orig = (HOST, PORT)
tcp.bind(orig)	#Coloca um endereço local, endereço IP e porta, no socke
tcp.listen(5)	#Instrui o sistema operacional para colocar o socket em modo passivo

#VARIAVEIS GLOBAIS
dicDisp = {} #Dicionário de dispostivos {ID : [tipo,local,status,socket]}
id_dispositivo = 99 #ID dos dispostivos
temperatura = 26
presenca=0

def estabelecer_conexao(conexao,cliente,id_dispositivo):
	global dicDisp
	global temperatura
	global presenca
	print('\nConexão estabelecida por', cliente,end='')
	dados=[0,0]
	
	while True:
		msg = conexao.recv(1024) #aguarda dispositivo
		if not msg: break #encerra loop
		
		#// gera hora e data  
		dataehora = datetime.now()
		#//edita a hora
		dtbuff=dataehora.strftime('%d/%m/%Y %H:%M:%S')
		
		if id_dispositivo not in dicDisp: #Quando o dispositivo é novo entra nesse if
			print('\n%s'%(dtbuff)) #imprime data/hora
			print('Cliente:',msg.decode())
			local = input('Informe a localização do(a) '+ msg.decode() +': ')
			status=''
			
			dicDisp[id_dispositivo] = [msg.decode(),local,status,conexao] #adiciona dispositivo ao dicionario
			conexao.send(str(id_dispositivo).encode()) #envia a ID para o dispositivo
			
		else:
			dados[0],dados[1]=struct.unpack_from("ii",msg) #Desenpacota a struct dentro de msg
		#============SENSOR DE PRESENÇA===========================
		if dados[0] in dicDisp and dicDisp[dados[0]][0]=='Sensor de Presença':
		
			#dados=[0,0] #[ID,satus]
			
			CNXLamp=0
			
			dados[0],dados[1]=struct.unpack_from("ii",msg) #Desenpacota a struct dentro de msg
			status=dados[1] #status 1 ou 0
			ID=dados[0] #ID do sensor
			local=dicDisp[ID][1] #puxa o local do dicionário
			
			#// gera hora e data  
			dataehora = datetime.now()
			#//edita a hora
			dtbuff=dataehora.strftime('%d/%m/%Y %H:%M:%S')
			
			
			
			if status == 0:
				print('\n%s'%(dtbuff))#imprime data/hora
				print("Sensor %i: %s vazio"%(ID,local))
				dicDisp[id_dispositivo][2] = 'Desatuado' #Altera status do dicionario
			if status == 1:
				print('\n%s'%(dtbuff))#imprime data/hora
				print("Sensor %i: Pessoa detectada no(a) %s"%(ID,local))
				dicDisp[id_dispositivo][2] = 'Atuado' #Altera status do dicionario

			for i in dicDisp: #loop para buscar a lâmpada referente a esse sensor
				if dicDisp[i][0] == 'Lâmpada' and dicDisp[i][1] == local: #precisa ser do tipo lâmpada e ser do mesmo lugar
					CNXLamp=dicDisp[i][3] #pega o socket da lâmpada
			
			if CNXLamp != 0:
				CNXLamp.send(str(status).encode()) #Envia novo status para lampada
				
	
		#===================TERMÔMETRO===========================
		if dados[0] in dicDisp and dicDisp[dados[0]][0]=='Termômetro':
			
			
			dados[0],dados[1]=struct.unpack_from("ii",msg) #Desenpacota a struct dentro de msg
			temperatura=dados[1]
			ID=dados[0]
			local=dicDisp[ID][1]
			CNXar=0
			
			dicDisp[ID][2] = temperatura #Altera status do dicionario
			
			#// gera hora e data  
			dataehora = datetime.now()
			#//edita a hora
			dtbuff=dataehora.strftime('%d/%m/%Y %H:%M:%S')
			
			print('\n%s'%(dtbuff))#imprime data/hora
			print("Termômetro %i: %s °C no(a) %s"%(ID,temperatura,local))
			
			for i in dicDisp: #loop para buscar o socket do ar-condicionado de local específico
				if dicDisp[i][0] == 'Ar-Condicionado' and dicDisp[i][1] == local:
					CNXar=dicDisp[i][3]
			
			if temperatura >= 28 and CNXar != 0:
				Sstatus=struct.pack('iii',temperatura,1,22) #empacota status e temperatura
				CNXar.send(Sstatus) #Envia novo status para Ar-Condicionado
			elif temperatura < 22 and CNXar != 0:
				Sstatus=struct.pack('iii',temperatura,0,22) #empacota status e temperatura
				CNXar.send(Sstatus) #Envia novo status para Ar-Condicionado
		
		#===================AR-CONDICIONADO===========================
		if dados[0] in dicDisp and dicDisp[dados[0]][0]=='Ar-Condicionado':
			tempBuff=0
			
			dataehora = datetime.now()
			if tempBuff != temperatura:#para nao ficar imprimindo o loop a cada segundo, apenas se temperatura mudar
				if (dataehora.hour == 18 and dataehora.minute == 00 and dataehora.second == 00): #liga o ar se der 18:00:00 em ponto
					tempBuff=temperatura
					Sstatus=struct.pack('ii',temperatura,1) #empacota status e temperatura
					dicDisp[dados[0]][3].send(Sstatus) #Envia novo status para Ar-Condicionado
				#time.sleep(1) #espera um segundo

		#===================TOMADA===========================
		if dados[0] in dicDisp and dicDisp[dados[0]][0]=='Tomada':
			#// gera hora e data  
			dataehora = datetime.now()
			#//edita a hora
			dtbuff=dataehora.strftime('%d/%m/%Y %H:%M:%S')
			
			concatena = dicDisp[dados[0]][0]+str(dados[0])
			arq = open(concatena + ".txt", 'a')
			arq.write(str('Consumo na tomada em %s: %sW')%(dtbuff,dados[1])+"\n")
			dicDisp[dados[0]][2] = dados[1] #Altera status do dicionario
			
			
			
			print('\n%s'%(dtbuff))#imprime data/hora
			print("Tomada %i: Consumo é %i W no(a) %s"%(dados[0],dados[1],dicDisp[dados[0]][1])) #imprime consumo
			arq.close()
	time.sleep(1) #espera um segundo
	print('\n%s'%(dtbuff))#imprime data/hora
	print('Finalizando conexao do(a)')

	conexao.close()
	thread.exit()

print("SERVIDOR ONLINE")
while True:
	conexao,cliente = tcp.accept() #Aceita uma nova conexão
	id_dispositivo += 1 #incrementa a ID do novo cliente
	thread.start_new_thread(estabelecer_conexao, (conexao,cliente,id_dispositivo)) #Cria uma thread para cada dispositivo


tcp.close()



if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
