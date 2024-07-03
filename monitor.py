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


# FASE 3: inserire parametri temporali e definire funzioni 
#         che dicono se market è aperto o chiuso

open_day_1 = time.time()#1719475200
close_day_1 = open_day_1 + 9 * 3600
open_day_2 = close_day_1 + 15 * 3600
close_day_2 = open_day_2 + 9 * 3600
open_day_3 = close_day_2 + 15 * 3600
close_day_3 = open_day_3 + 9 * 3600
open_day_4 = close_day_3 + 15 * 3600
close_day_4 = open_day_4 + 9 * 3600
open_day_5 = close_day_4 + 15 * 3600
close_day_5 = open_day_5 + 9 * 3600

def is_open():
	t = time.time()
	return ((t > open_day_1 and t < close_day_1) or
		(t > open_day_2 and t < close_day_2) or
		(t > open_day_3 and t < close_day_3) or
		(t > open_day_4 and t < close_day_4) or
		(t > open_day_5 and t < close_day_5))

def rush_finale():
	t = time.time()
	return (t > close_day_5-60*10 and t < close_day_5)

def inizio():
	t = time.time()
	return (t > open_day_1 and t < open_day_1 + 60*10)


# FASE 4: Programma vero e proprio di monitoring
#         Scrive su un file le informazioni ogni 5 minuti quando il mercato è aperto
#         e ogni 30 secondi nei primi e negli ultimi 10 min di gara
def main():

	# apre file di scrittura
	f = open('data.txt', 'w')
    
	#ciclo while che si arresta solo dopo alla chiusura della gara
	end=0
	while (end == 0): 

		try:
			tempo = time.time()
			if tempo>close_day_5:
				end=1
			# segna i dati delle singole pool
			tokenpool = []
			liquiditypool = []
			pricepool = []
			kpool = []
			for i in range(3):
				tokenpool.append(token[i].balanceOf(marketplace_address)/ 1e18)
				liquiditypool.append(marketplace.liquidity(token_address[i]) / 1e18)
				pricepool.append(marketplace.price(token_address[i])/ 1e18)
				kpool.append(marketplace.k(token_address[i]) / 1e36)
				
			# segna i dati del wallet delle tre squadre (i) ciclando sui tre token (j)
			tokenowners =[]
			paycoinowners =[]
			for i in range(3):
				for j in range(3):
					tokenowners.append(token[j].balanceOf(user_address[i]) / 1e18)
				paycoinowners.append(paycoin.balanceOf(user_address[i]) / 1e18)

			#preparo riga

			riga = [tempo, 
			        tokenpool[0], liquiditypool[0], pricepool[0], kpool[0],
				tokenpool[1], liquiditypool[1], pricepool[1], kpool[1],
				tokenpool[2], liquiditypool[2], pricepool[2], kpool[2],
				paycoinowners[0], tokenowners[0], tokenowners[1], tokenowners[2],
				paycoinowners[1], tokenowners[3], tokenowners[4], tokenowners[5],
				paycoinowners[2], tokenowners[6], tokenowners[7], tokenowners[8]]
			
			for i in range(len(riga)):
				 f.write(str(riga[i]) + ' ')    
		f.write('\n')
			print('monitoring ok')
		
		except:

			print('something went wrong')
  
		# prima di ricominciare il while diamo un delay temporale per raccogliere dati 
		# di continuo ma solo ogni 5 minuti quando il mercato è aperto, e ogni 30 secondi
		# durante il rush finale o l'inizio
		if (is_open()):
			if(rush_finale() or inizio()):
				time.sleep(30)
			else:
				time.sleep(5 * 60)
		else:
			time.sleep(15 * 3600)

    # chiudo il file
	f.close()

if __name__ == "__main__":
    main()