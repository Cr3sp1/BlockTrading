from brownie import Paycoin, accounts

acct = accounts.add('0xd666d5d86ec4985742a02c9976d0c6ff3a820f06c94e5213c9c25a49a22a150e')

def mint_pc():

	Paycoin[0].mint('0xE9243393dBD3B756958aE75f9047D72D16b10B5d', 55000 * 1e18, {'from': acct})
	Paycoin[0].mint('0x7291A5E495D585f81D6c07E4e3336bb0bc3cF1ce', 55000 * 1e18, {'from': acct})
	Paycoin[0].mint('0x0EDe86A8944925D1510215717B62659C33662743', 55000 * 1e18, {'from': acct})


def add_minters():

	Paycoin[0].add_minter(acct, {'from': acct})
	Paycoin[0].add_minter('0x9ABf4d1337838786e68bCEF9CFD12d9FC45C2Ecf', {'from': acct})
	Paycoin[0].add_minter('0x910698d55903456B22006a0b4004Fd90687aC647', {'from': acct})
	Paycoin[0].add_minter('0xF76CAcF83bC5963c68928c99ce0593720D8dC132', {'from': acct})
