import csv

from brownie import web3
from web3.exceptions import BadResponseFormat
from brownie import accounts, network, exceptions, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace, Challenge
network.connect('development')
#network.connect('ganache-local')

def reward_challenger(type, challenger_symb):

    owner_idx = token_symbols.index(challenger_symb)
    owner = token_owners[owner_idx]

    match type:

        case "1v1":

            token_list[0].minting(owner, 1000 * 1e18, {'from': challenge})
            
        case "1v2":
            
            token_list[0].minting(owner, 2000 * 1e18, {'from': challenge})

def reward_winner(type, winner_symb):

    owner_idx = token_symbols.index(winner_symb)
    owner = token_owners[owner_idx]

    match type:

        case "1v1":

            token_list[0].minting(owner, 10000 * 1e18, {'from': challenge})
            
        case "1v2":
            
            token_list[0].minting(owner, 50000 * 1e18, {'from': challenge})

def load_contracts():

    global challenge
    global token_list, token_owners, token_symbols

    token_list = []
    token_owners = [] 
    token_symbols = []

    try:

        with open(brownie_dir + 'contracts_addr.txt', 'r') as token_addr_f:

            for i in range(4):

                token_addr = str(token_addr_f.readline().strip('\n'))
                token_list.append(Token.at(token_addr))

        with open(brownie_dir + 'challenge_addr.txt', 'r') as address_file: 

            challenge_address = address_file.readline().strip('\n')
        
        token_owners = [token.owner() for token in token_list[1:]]
        token_symbols = [token.symbol() for token in token_list[1:]]
        challenge = Challenge.at(challenge_address)

    except exceptions.ContractNotFound:
        print("Contracts not found. Maybe you forgot to run deploy?")
        import sys
        sys.exit()

def main():

    load_contracts()

    challenge_log_f = open('challenge_log.csv', 'r+')
    challenge_hist_f = open('challenge_hist.csv', 'a')

    csv_reader = csv.reader(challenge_log_f, delimiter=',')
    csv_writer = csv.writer(challenge_hist_f, delimiter=',')

    for row in csv_reader:
        
        csv_writer.writerow(row)

        type = row[0]
        challenger_sym = row[1]
        winner_sym = row[3]

        reward_challenger(type, challenger_sym)
        reward_winner(type, winner_sym)


    challenge_log_f.truncate(0)

    challenge_log_f.close()
    challenge_hist_f.close()


if __name__ == "__main__":
    main()