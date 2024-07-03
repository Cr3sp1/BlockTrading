from brownie import accounts, network, exceptions, Contract, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace
network.connect('ganache-local')

import random
import time

#open_day_1 = 1719475200
open_day_1 = time.time() # DEBUG only
close_day_1 = open_day_1 + 9 * 3600
open_day_2 = open_day_1 + 24 * 3600 
close_day_2 = open_day_2 + 9 * 3600
open_day_3 = open_day_2 + 24 * 3600
close_day_3 = open_day_3 + 9 * 3600
open_day_4 = open_day_3 + 48 * 3600
close_day_4 = open_day_4 + 9 * 3600
open_day_5 = open_day_4 + 24 * 3600
close_day_5 = open_day_5 + 9 * 3600

def load_contracts():

	token_list = []
	market = None

	try:

		with open(brownie_dir + 'contracts_addr.txt', 'r') as token_addr_f:

			for i in range(4):

				token_addr = str(token_addr_f.readline().strip('\n'))
				token_list.append(Token.at(token_addr))

		with open(brownie_dir + '/marketplace_addr.txt', 'r') as market_addr_f:

			market_addr = str(market_addr_f.readline().strip('\n'))
			market = Marketplace.at(market_addr)

	except exceptions.ContractNotFound:
		print("Contracts not found. Maybe you forgot to run deploy?")
		import sys
		sys.exit()

	return (token_list, market)

def add_bot():

	f = open(brownie_dir + 'private_keys.txt', 'r')

	for i in range(100):

		key = str(f.readline())
		accounts.add(key.strip('\n'))

	f.close()

def is_open():

    t = time.time()
	#print(time.asctime(time.gmtime(t)))

    return ((t > open_day_1 and t < close_day_1) or
        (t > open_day_2 and t < close_day_2) or
        (t > open_day_3 and t < close_day_3) or
        (t > open_day_4 and t < close_day_4) or
        (t > open_day_5 and t < close_day_5))

def main():

	add_bot()
	(token_list, market) = load_contracts()
	token_symbols = [token.symbol() for token in token_list[1:]]

	#for i in range(9, 109): # will be range(100)

		#for token in token_list:

			#token.increaseAllowance(1e30, market.address, {'from': accounts[i]})

	op_list = ["buy", "sell", "swap"]
	op_log_file = open("bot_log.txt", "w")

	while(time.time() < close_day_5):

		if(is_open()):

			token_idx = random.randint(1, 3)
			#bot_idx = random.randint(0, 99)
			bot_idx = random.randint(9, 109) # TEST ONLY (10 ganache accounts)
			op_num = random.randint(0, 2)
			#op_num = 2

			match op_list[op_num]:

				case "buy":

					bot_balance = token_list[0].balanceOf(accounts[bot_idx], {'from': accounts[bot_idx]}) 
					print("Bot id: {}\tBalance: {}".format(bot_idx, bot_balance / 1e18))

					paycoin_amount = int(bot_balance * random.uniform(0.20, 0.80))

					token_list[0].increaseAllowance(paycoin_amount, market.address, {'from': accounts[bot_idx]})
					market.buy(token_list[token_idx].address, paycoin_amount, {'from': accounts[bot_idx]})

					op_log_file.write("{},{},{}PC\n".format(bot_idx, op_list[op_num], float(paycoin_amount) / 1e18))
					
				case "sell":

					token_balance = token_list[token_idx].balanceOf(accounts[bot_idx],{'from':accounts[bot_idx]})
					print("Bot id: {}\tBalance of Token: {}".format(bot_idx, token_balance / 1e18))

					token_amount = int(token_balance * random.uniform(0.20, 0.80))

					token_list[token_idx].increaseAllowance(token_amount, market.address, {'from': accounts[bot_idx]})
					market.sell(token_list[token_idx].address, token_amount,{'from': accounts[bot_idx]})

					op_log_file.write("{},{},{}{}\n".format(bot_idx, op_list[op_num], float(token_amount) / 1e18, token_symbols[token_idx - 1]))

				case "swap":
					
					token_idx2 = random.choice([num for num in range(1, 4) if num != token_idx])
					
					token_balance = token_list[token_idx].balanceOf(accounts[bot_idx],{'from':accounts[bot_idx]})
					token_balance2 = token_list[token_idx2].balanceOf(accounts[bot_idx],{'from':accounts[bot_idx]})
					print("Bot id: {}\tBalance of Token 1: {}".format(bot_idx, token_balance / 1e18))
					print("Bot id: {}\tBalance of Token 2: {}".format(bot_idx, token_balance2 / 1e18))

					token_amount = int(token_balance * random.uniform(0.20, 0.80))
					paycoin_amount = market.tokenToPaycoin( token_list[token_idx].address, token_amount )
					token_amount2 = market.paycoinToToken( token_list[token_idx2].address, paycoin_amount )


					token_list[token_idx].increaseAllowance(token_amount, market.address, {'from': accounts[bot_idx]})
					token_list[0].increaseAllowance(paycoin_amount, market.address, {'from': accounts[bot_idx]})
					market.swap(token_list[token_idx].address,token_list[token_idx2].address,token_amount,{'from': accounts[bot_idx]})

					op_log_file.write("{},{},{}{},{}{}\n".format(
						
						bot_idx, 
						op_list[op_num], 
						float(token_amount) / 1e18, 
						token_symbols[token_idx - 1],
						float(token_amount2) / 1e18,
						token_symbols[token_idx2 - 1]
						
						)
					)
					
		time.sleep(1)
    
	op_log_file.close()

if __name__ == "__main__":
    main()


    


