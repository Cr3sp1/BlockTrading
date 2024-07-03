from brownie import accounts, Contract, Paycoin
import random
import time
import json

with open('/home/daniele_atzori/Blockchain/esame/abi/Pool.json') as json_file:
	pool_abi = json.load(json_file)

pool1 = Contract.from_abi('Pool', '0x9ABf4d1337838786e68bCEF9CFD12d9FC45C2Ecf', pool_abi)
pool2 = Contract.from_abi('Pool', '0x910698d55903456B22006a0b4004Fd90687aC647', pool_abi)
pool3 = Contract.from_abi('Pool', '0xF76CAcF83bC5963c68928c99ce0593720D8dC132', pool_abi)

pool_address = [pool1, pool2, pool3]


with open('/home/daniele_atzori/Blockchain/esame/abi/Token.json') as json_file:
	token_abi = json.load(json_file)

token1 = Contract.from_abi('Token', '0x6e2D42431BD5b67bC2D6141b904ca29c7db15991', token_abi)
token2 = Contract.from_abi('Token', '0xfFCB7bE21756e6f4e2cd4b5d2D5123aa4fB2878a', token_abi)
token3 = Contract.from_abi('Token', '0xd935672e5f72f4aBb64866ee9D14eB0f98E887E5', token_abi)

token_address = [token1, token2, token3]


open_day_1 = 1689577200
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


def add_bot():

	f = open('private_keys.txt', 'r')

	for i in range(100):

		key = str(f.readline())
		accounts.add(key.strip('\n'))

	f.close()


def work_bot():

	while (True):

		try:

			n = random.randint(0,2)
			m = random.randint(1,100)

			pay = Paycoin[0].balanceOf(accounts[m], {'from': accounts[m]}) / 1e18
			tok_max = pay * 1e18 / pool_address[n].view_price({'from': accounts[m]})
			Paycoin[0].approve(pool_address[n], pay, {'from': accounts[m]})
			tok_am = random.randint(0, tok_max/10)
			pool_address[n].buy(tok_am, {'from': accounts[m]})

			tok_max = token_address[n].balanceOf(accounts[m], {'from': accounts[m]}) / 1e18
			token_address[n].approve(pool_address[n], tok_max, {'from': accounts[m]})
			tok_am = random.randint(0, tok_max/10)
			pool_address[n].sell(tok_am, {'from': accounts[m]})

			print('succeeded')

		except:

			print('failed')


		if (is_open()):
			time.sleep(60)

		else:
			time.sleep(15 * 3600)
