from brownie import accounts, Token
import random

account_padre = accounts[0]

def main():
	#account_padre = accounts.add('Indirizzo owner marketplace')
	create_accounts()
	mint_bot()


def create_accounts():

	fpu = open('public_keys.txt', 'w')
	fpr = open('private_keys.txt', 'w')

	for i in range(100):

		account = accounts.add()
		fpr.write(account.private_key + '\n')
		fpu.write(str(account) + '\n')

	fpu.close()
	fpr.close()
	
def mint_bot():

	f = open('public_keys.txt', 'r')

	for i in range(100):

		account = f.readline()
		Token[0].minting(str(account.strip('\n')), random.randint(1000, 100000) * 1e18, {'from': account_padre})
		account_padre.transfer(str(account.strip('\n')), "100 finney")

	f.close()



