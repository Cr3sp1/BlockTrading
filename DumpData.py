import csv
from brownie import accounts, network, exceptions, Contract, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace, Challenge
network.connect('ganache-local')

def load_contracts():

    global token_list, token_owners, token_symbols, market

    token_list = []
    token_owners = [] 
    token_symbols = []
    market = None   

    try:

        with open(brownie_dir + 'contracts_addr.txt', 'r') as token_addr_f:

            for i in range(4):

                token_addr = str(token_addr_f.readline().strip('\n'))
                token_list.append(Token.at(token_addr))

        with open(brownie_dir + '/marketplace_addr.txt', 'r') as market_addr_f:

            market_addr = str(market_addr_f.readline().strip('\n'))
            market = Marketplace.at(market_addr)

        token_owners = [token.owner() for token in token_list[1:]]
        token_symbols = [token.symbol() for token in token_list[1:]]

    except exceptions.ContractNotFound:
        print("Contracts not found. Maybe you forgot to run deploy?")
        import sys
        sys.exit()

def main():

    load_contracts()

    dump_f_main = open('net_main_accounts_dump.csv', 'w')
    writer_main = csv.writer(dump_f_main, delimiter=',')

    for index, account in enumerate(accounts):

        data = [index]

        for token in token_list:

            data.append(token.balanceOf(account.address, {'from': accounts[0]}))

        writer_main.writerow(data)

    dump_f_main.close()

    dump_f_bots = open("net_bots_accounts_dump.csv", 'w')
    writer_bots = csv.writer(dump_f_bots, delimiter=',')
    public_keys = open("./Brownie/public_keys.txt", 'r')
    addresses = public_keys.readlines()

    for index, address in enumerate(addresses):

        data = [index]

        for token in token_list:

            data.append(token.balanceOf(address.strip('\n'), {'from': accounts[0]}))

        writer_bots.writerow(data)

    dump_f_bots.close()
    public_keys.close()

    dump_f_market = open("net_markte_dump.csv", 'w')
    writer_market = csv.writer(dump_f_market, delimiter=',')

    data = [0]

    for token in token_list:

        data.append(token.balanceOf(market.address, {'from': accounts[0]}))

    writer_market.writerow(data)

    dump_f_market.close()

if __name__ == "__main__":
    main()

