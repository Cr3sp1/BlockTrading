import time
import json

from brownie import web3
from web3.exceptions import BadResponseFormat
from brownie import accounts, network, exceptions, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace, Challenge
network.connect('ganache-local')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.switch_backend('TkAgg')

# FASE 1: recuperare tutti gli indirizzi: token, paycoin, pool, users

with open(brownie_dir + 'contracts_addr.txt', 'r') as address_file: 
	token_address= []
	paycoin_address = address_file.readline().strip('\n')
	for i in range(3):
		appo = str(address_file.readline().strip('\n'))
		token_address.append(appo)

with open(brownie_dir + 'marketplace_addr.txt', 'r') as address_file: 
	marketplace_address = address_file.readline().strip('\n')


# FASE 2: assegnare contratti deployati

marketplace = Marketplace.at(marketplace_address)

token1 = Token.at(token_address[0])
token2 = Token.at(token_address[1])
token3 = Token.at(token_address[2])
token = [token1, token2, token3]
symbol = [token1.symbol(), token2.symbol(), token3.symbol()] 

paycoin = Token.at(paycoin_address) 

# INDIRIZZI NOSTRI
user_address = [token1.owner(), token2.owner(), token3.owner()]
user_names = ['Team1', 'Team2', 'Team 3']


# FASE 4: Programma vero e proprio di monitoring
#         Scrive su un file le informazioni ogni 5 minuti quando il mercato è aperto
#         e ogni 30 secondi nei primi e negli ultimi 10 min di gara
def main():

	tempo = time.time()
	tokenpool = []
	liquiditypool = []
	pricepool = []
	kpool = []

	for i in range(3):
		tokenpool.append(token[i].balanceOf(marketplace_address)/ 1e18)
		liquiditypool.append(marketplace.liquidity(token_address[i]) / 1e18)
		pricepool.append(marketplace.price(token_address[i])/ 1e18)
		kpool.append(marketplace.k(token_address[i]) / 1e36)

	tokenowners =[]
	paycoinowners =[]

	for i in range(3):
		for j in range(3):
			tokenowners.append(token[j].balanceOf(user_address[i]) / 1e18)
		paycoinowners.append(paycoin.balanceOf(user_address[i]) / 1e18)

	print('MONITORING:\n\n\n\n')

	for i in range(3):

		print('POOL ' + str(i+1) + ':\n')
		print('Token in pool: '+ str(tokenpool[i]) +' token\n')
		print('Paycoin in pool: '+ str(liquiditypool[i]) + ' paycoin\n')
		print('Prezzo token: ' + str(pricepool[i]) + ' paycoin su token \n')
		print('k: ' + str(kpool[i]) + ' paycoin per token \n')
		print('\n')

	for i in range(3):
		print('WALLET ' + str(i+1) + ':\n')
		print('Paycoin: ' + str(paycoinowners[i]) + ' paycoin\n' )
		for j in range(3):
			print('Token ' + str(j+1) + ': ' + str(tokenowners[3*i+j]) + ' token\n' )

	# GRAFICI

	# Creazione del grafico
	fig, axs = plt.subplots(1, 3, figsize=(18, 6))	

	paycoininit= 100000
	tokeninit_vector =[100,10000, 1000000]

	for i in range(3):

		k= kpool[i]
		m=pricepool[i]
		tokeninit=tokeninit_vector[i]

		start=1
		stop=3*tokeninit

		t = np.linspace(start,stop, 400)
		iperbole=k/t
		retta= m*t

		axs[i].plot(t, iperbole, label='external market', color='blue')
		axs[i].plot(t, retta, label='internal market', color='red')

		axs[i].plot(tokeninit, paycoininit, 'go', label='Stato iniziale')
		axs[i].plot(tokenpool[i], liquiditypool[i], 'go', label='Stato attuale')

		axs[i].axvline(x=0.5*tokeninit, color='purple', linestyle='--', label='limite inferiore mercato interno')
		axs[i].axvline(x=2*tokeninit, color='orange', linestyle='--', label='limite superiore mercato interno')
    
		axs[i].set_xlabel('T')
		axs[i].set_ylabel('P')
    
		axs[i].set_xlim(0, 3*tokeninit)
		axs[i].set_ylim(0, 3*paycoininit)

		axs[i].legend()
		axs[i].grid(True)
		axs[i].set_title(f'Pool {i+1}')

	# Mostra il grafico
	plt.suptitle(f'Istante t={tempo}')
	plt.tight_layout()
	plt.subplots_adjust(top=0.9)
	plt.show()		

if __name__ == "__main__":
    main()