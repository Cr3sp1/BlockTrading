from brownie import accounts, Contract, Paycoin
import json
import random

acct = accounts.add('0xd666d5d86ec4985742a02c9976d0c6ff3a820f06c94e5213c9c25a49a22a150e')

def create_accounts():

	fpu = open('public_keys.txt', 'w')
	fpr = open('private_keys.txt', 'w')

	for i in range(99):

		account = accounts.add()
		fpr.write(account.private_key + '\n')
		fpu.write(str(account) + '\n')

	fpu.close()
	fpr.close()


def mint_bot():

	f = open('public_keys.txt', 'r')

	for i in range(100):

		account = f.readline()
		Paycoin[0].mint(str(account.strip('\n')), random.randint(1000, 100000) * 1e18, {'from': acct})

	f.close()


def distribute_eth():

	f = open('public_keys.txt', 'r')

	for i in range(100):

		account = f.readline()
		acct.transfer(str(account.strip('\n')), '100 finney')

	f.close()
