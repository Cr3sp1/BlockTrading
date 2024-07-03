import asyncio
from brownie import accounts, network, exceptions, Contract, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Marketplace
network.connect('ganache-local')


# Addresses
MYTOKEN_CONTRACT_ADDRESS = "0xYourTokenContractAddress"
account = "0xYourAddress"

with open(brownie_dir + '/marketplace_addr.txt', 'r') as market_addr_f:

			market_addr = str(market_addr_f.readline().strip('\n'))
			market = Marketplace.at(market_addr)

market.day_mint(MYTOKEN_CONTRACT_ADDRESS, {'from':account})