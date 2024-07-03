from brownie import accounts, Contract, Paycoin
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

user_address = ['0xE9243393dBD3B756958aE75f9047D72D16b10B5d',
		'0x7291A5E495D585f81D6c07E4e3336bb0bc3cF1ce',
		'0x0EDe86A8944925D1510215717B62659C33662743']

user_names = ['Giovanni', 'Daniele', 'Paolo']

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


def monitor():

	acct = accounts.add('0xd666d5d86ec4985742a02c9976d0c6ff3a820f06c94e5213c9c25a49a22a150e')

	f = open('data.txt', 'w')
	f.write("MONITORING:\n\n\n\n")

	while (True):

		try:

			f.write("Time stamp:" + str(time.time()) + "\n\n")

			for i in range(3):

				pool_add = pool_address[i]
				symbol = token_address[i].symbol({'from': acct})
				f.write('Pool ' + symbol + ' stake:\n')
				f.write(str(pool_add.view_token_amount({'from': acct}) / 1e18) + symbol + '\n')
				f.write(str(pool_add.view_paycoin_amount({'from': acct}) / 1e18) + 'PC\n')
				f.write('Price:\n')
				f.write(str(pool_add.view_price({'from': acct}) / 1e18) + 'PC/' + symbol + '\n\n')


			for i in range(3):

				address = user_address[i]

				f.write('Balances of ' + user_names[i] + ':\n')

				for j in range(3):

					symbol = token_address[j].symbol({'from': acct})
					f.write('Token' + symbol + ': ' + str(token_address[j].balanceOf(address, {'from': acct}) / 1e18) + '\n')

				f.write('Paycoin: ' + str(Paycoin[0].balanceOf(address, {'from': acct}) / 1e18) + '\n\n\n')

			print('monitoring is ok')

		except:

			print('something went wrong')


		if (is_open()):
			time.sleep(15 * 60)

		else:
			time.sleep(15 * 3600)

	f.close()
