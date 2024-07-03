from brownie import accounts, Paycoin

def deploy_pc():

	acct = accounts.add('0xd666d5d86ec4985742a02c9976d0c6ff3a820f06c94e5213c9c25a49a22a150e')
	Paycoin.deploy('Paycoin', 'PC', 18, 0, {'from': acct})
