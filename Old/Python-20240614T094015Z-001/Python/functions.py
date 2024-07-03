from brownie import Pool, Token, accounts, Contract
from sys import exit
import json

with open('/home/daniele_atzori/Blockchain/esame/abi/Paycoin.json') as json_file:

	pc_abi = json.load(json_file)

pc = Contract.from_abi('Paycoin', '0x85f294A64142a38563c1f38A2946b147AE4aD8a6', pc_abi)


with open('/home/daniele_atzori/Blockchain/esame/abi/Pool.json') as json_file:
	pool_abi = json.load(json_file)

pool1 = Contract.from_abi('Pool', '0x9ABf4d1337838786e68bCEF9CFD12d9FC45C2Ecf', pool_abi)
pool2 = Pool[1]
pool3 = Contract.from_abi('Pool', '0xF76CAcF83bC5963c68928c99ce0593720D8dC132', pool_abi)

pool_address = [pool1, pool2, pool3]


with open('/home/daniele_atzori/Blockchain/esame/abi/Token.json') as json_file:
	token_abi = json.load(json_file)

token1 = Contract.from_abi('Token', '0x6e2D42431BD5b67bC2D6141b904ca29c7db15991', token_abi)
token2 = Token[0]
token3 = Contract.from_abi('Token', '0xd935672e5f72f4aBb64866ee9D14eB0f98E887E5', token_abi)

token_address = [token1, token2, token3]


user_address = ['0xE9243393dBD3B756958aE75f9047D72D16b10B5d',
		'0x7291A5E495D585f81D6c07E4e3336bb0bc3cF1ce',
		'0x0EDe86A8944925D1510215717B62659C33662743']

user_names = ['Giovanni', 'Daniele', 'Paolo']


def monitor_pool(symbol):

	pool_add = pool_address[token_type(symbol)]
	print('Pool ' + symbol + ' stake:')
	print(str(pool_add.view_token_amount({'from': accounts[0]}) / 1e18) + symbol)
	print(str(pool_add.view_paycoin_amount({'from': accounts[0]}) / 1e18) + 'PC')
	print('Price:')
	print(str(pool_add.view_price({'from': accounts[0]}) / 1e18) + 'PC/' + symbol)



def get_address(name):

	stat = False

	for i in range(3):

		if ((stat == False) and (name == user_names[i])):

			n = i
			stat = True

	if ( stat == False ):

		exit('The name is not valid!')

	return user_address[n]


def balance(name):

	address = get_address(name)

	print('Balances of ' + name + ':')

	for i in range(3):

		symbol = token_address[i].symbol({'from': accounts[0]})
		print('Token ' + symbol + ': ' + str(token_address[i].balanceOf(address, {'from': accounts[0]}) / 1e18))

	print('Paycoin: ' + str(pc.balanceOf(address, {'from': accounts[0]}) / 1e18))


def my_balance():

	print('Your balance:')

	for i in range(3):

		symbol = token_address[i].symbol({'from': accounts[0]})
		print('Token ' + symbol + ': ' + str(token_address[i].balanceOf(accounts[0], {'from': accounts[0]}) / 1e18))

	print('Paycoin: ' + str(pc.balanceOf(accounts[0], {'from': accounts[0]}) / 1e18))


def day_mint():

	Pool[1].day_mint({'from': accounts[0]})


def mint_stake(token_amount):


	paycoin_am = pc.balanceOf(accounts[0], {'from': accounts[0]}) / 1e18
	pc.approve(Pool[1], paycoin_am, {'from': accounts[0]})
	Pool[1].mint_stake(token_amount, {'from': accounts[0]})


def burn_stake(token_amount):

	#Token[0].approve(token_amount, {'from': accounts[0]})
	Pool[1].burn_stake(token_amount, {'from': accounts[0]})


def token_type(symbol):

	stat = False

	for i in range(3):

		if ((symbol == token_address[i].symbol({'from': accounts[0]})) and (stat == False)):

			n = i
			stat = True

	if ( stat == False ):

		exit('Not valid token!')

	return n


def buy(token, type):

	pool_n = token_type(type)
	pool_add = pool_address[pool_n]
	paycoin_am = pc.balanceOf(accounts[0], {'from': accounts[0]}) / 1e18

	pc.approve(pool_add, paycoin_am, {'from': accounts[0]})

	pool_add.buy(token, {'from': accounts[0]})


def sell(token, type):

	pool_n = token_type(type)
	pool_add = pool_address[pool_n]
	token_add = token_address[pool_n]

	token_add.approve(pool_add, token, {'from': accounts[0]})

	pool_add.sell(token, {'from': accounts[0]})


def converter(type1, type2):

	pool_n1 = token_type(type1)
	pool_n2 = token_type(type2)
	pool_add1 = pool_address[pool_n1]
	pool_add2 = pool_address[pool_n2]
	converter = pool_add1.view_price({'from': accounts[0]}) / pool_add2.view_price({'from': accounts[0]})

	print(converter)

	return converter


def swap_token(token1, type1, type2):

	c = converter(type1, type2)
	sell(token1, type1)
	buy(token1 * c, type2)
