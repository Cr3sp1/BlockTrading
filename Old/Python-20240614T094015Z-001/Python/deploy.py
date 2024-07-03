from brownie import Token, Pool, accounts, Contract
import json

with open('/home/daniele_atzori/Blockchain/esame/abi/Paycoin.json') as json_file:

	pc_abi = json.load(json_file)

pc = Contract.from_abi('Paycoin', '0x85f294A64142a38563c1f38A2946b147AE4aD8a6', pc_abi)

acct = accounts.load('atzo')

def deploy():

	token = Token.deploy("TokenDA", "DA", 18, 500, {'from': acct})
	Pool.deploy(token, pc, {'from': acct})


def init_pool():

	Pool[1].add_address(Pool[1], {'from': acct})
	Token[0].add_minter(Pool[1], {'from': acct})
	Pool[1].mint_liquidity(10000, 100000, {'from': acct})
