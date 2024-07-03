from brownie import accounts, Token, Marketplace, Challenge

def main():
    MarketOwner = accounts[0]
    TokenAOwner = accounts[1]
    TokenBOwner = accounts[2]
    TokenCOwner = accounts[3]

    initialTokensA = 100 * 1e18
    initialTokensB = 10000 * 1e18
    initialTokensC = 1000000 * 1e18

    # Deploy tokens
    Paycoin = Token.deploy(MarketOwner, "Paycoin", "PC", {'from': MarketOwner})
    TokenA = Token.deploy(TokenAOwner, "Pepsi Coin", "LDR", {'from': TokenAOwner})
    TokenB = Token.deploy(TokenBOwner, "Quantum Coin", "QTC", {'from': TokenBOwner})
    TokenC = Token.deploy(TokenCOwner, "Book of Ra", "BOR", {'from': TokenCOwner})

    # Deploy marketplace
    Market = Marketplace.deploy(MarketOwner, Paycoin.address, {'from': MarketOwner})

    #  Deploy challlenge
    Challenges = Challenge.deploy( Paycoin.address, {'from': MarketOwner})

    contract_addr_f = open('contracts_addr.txt', 'w')
    contract_addr_f.write(str(Paycoin.address) + '\n')
    contract_addr_f.write(str(TokenA.address) + '\n')
    contract_addr_f.write(str(TokenB.address) + '\n')
    contract_addr_f.write(str(TokenC.address) + '\n')
    contract_addr_f.close()

    market_addr_f = open('marketplace_addr.txt', 'w')
    market_addr_f.write(str(Market.address) + '\n')
    market_addr_f.close()

    challenge_addr_f = open('challenge_addr.txt', 'w')
    challenge_addr_f.write(str(Challenges.address) + '\n')
    challenge_addr_f.close()


    # Set MarketOwner as minter for all tokens
    Paycoin.setMinter(Market.address, {'from': MarketOwner})
    TokenA.setMinter(Market.address, {'from': TokenAOwner})
    TokenB.setMinter(Market.address, {'from': TokenBOwner})
    TokenC.setMinter(Market.address, {'from': TokenCOwner})

    # Set Challenge as minter for paycoin
    Paycoin.setMinter(Challenges.address, {'from': MarketOwner})

    # Now add tokens to the marketplace
    Market.addToken(TokenA.address, initialTokensA, {'from': MarketOwner})
    Market.addToken(TokenB.address, initialTokensB, {'from': MarketOwner})
    Market.addToken(TokenC.address, initialTokensC, {'from': MarketOwner})

    # Get and print info for verification
    print( "Market: ")
    print_info(Market.address, Paycoin, TokenA, TokenB, TokenC)
    print("Market liquidity pools: ")
    print(f"Pool A: {Market.liquidity(TokenA.address)/10**18}, Pool B: {Market.liquidity(TokenB.address)/10**18}, Pool C: {Market.liquidity(TokenC.address)/10**18}")
    print( "MarketOwner: ")
    print_info(MarketOwner, Paycoin, TokenA, TokenB, TokenC)
    print( "TokenAOwner: ")
    print_info(TokenAOwner, Paycoin, TokenA, TokenB, TokenC)
    print( "TokenBOwner: ")
    print_info(TokenBOwner, Paycoin, TokenA, TokenB, TokenC)
    print( "TokenCOwner: ")
    print_info(TokenCOwner, Paycoin, TokenA, TokenB, TokenC)
    print( "Other accounts: ")
    for account in accounts:
        print_info(account, Paycoin, TokenA, TokenB, TokenC)



def print_info(account, Paycoin, TokenA, TokenB, TokenC):
    balanceP = Paycoin.balanceOf(account) / 10**18
    balanceA = TokenA.balanceOf(account) / 10**18
    balanceB = TokenB.balanceOf(account) / 10**18
    balanceC = TokenC.balanceOf(account) / 10**18
    print(f"{account}: \tPC: {balanceP} \tTA: {balanceA} \tTB: {balanceB} \tTC: {balanceC}")


