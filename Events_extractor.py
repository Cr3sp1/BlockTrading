import csv
from brownie import web3
from web3.exceptions import BadResponseFormat
from brownie import accounts, network, exceptions, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace
# network.connect('development')
print("Connecting...")
network.connect('ganache-local')
print("Connection succcessful!")

# FASE 1: recuperare tutti gli indirizzi: token, paycoin, pool, users

with open(brownie_dir + 'contracts_addr.txt', 'r') as address_file: 
	token_address= []
	paycoin_address = address_file.readline().strip('\n')
	for i in range(3):
		appo = str(address_file.readline().strip('\n'))
		token_address.append(appo)

with open(brownie_dir + 'marketplace_addr.txt', 'r') as address_file: 
	marketplace_address = address_file.readline().strip('\n')


# FASE 2: assegnare contratti deployati

marketplace = Marketplace.at(marketplace_address)

token1 = Token.at(token_address[0])
token2 = Token.at(token_address[1])
token3 = Token.at(token_address[2])
token = [token1, token2, token3]
symbol = [token1.symbol(), token2.symbol(), token3.symbol()] 

paycoin = Token.at(paycoin_address)

block_num = web3.eth.block_number
print(f"Total blocks: {block_num+1}")

def loadEvents(eventType, stepSize, contract):
    last_event = stepSize - 1
    events = contract.events.get_sequence(from_block=0, to_block=last_event, event_type = eventType)
    block_num = web3.eth.block_number

    while(block_num > last_event):
        last_event = min(last_event + stepSize ,block_num)
        new_events = contract.events.get_sequence(from_block=last_event - stepSize + 1, to_block= last_event, event_type = eventType)
        events.extend(new_events)
        print(f"Up to {last_event}")
    

    return events


# Function to write events to CSV
def write_events_to_csv(events, filename, headers):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for event in events:
            writer.writerow([event['args'][header] for header in headers])

# Define headers for each event type
buy_headers = ["tokenAddress", "from", "tokenAmount", "paycoinAmount"]
sell_headers = ["tokenAddress", "from", "tokenAmount", "paycoinAmount"]
swap_headers = ["tokenAddressIn", "tokenAddressOut", "from", "tokenAmountIn", "tokenAmountOut", "paycoinAmount"]
day_mint_headers = ["tokenAddress", "tokenAmount"]
mint_headers = ["minter", "buyer", "value"]

# Write each event type to a separate CSV file
output_dir = './DATA/Events/'

events_buy = loadEvents("Buy", 1000, marketplace)
print("Events buy loaded!")
write_events_to_csv(events_buy, output_dir + 'events_buy.csv', buy_headers)

events_sell = loadEvents("Sell", 1000, marketplace)
print("Events sell loaded!")
write_events_to_csv(events_sell, output_dir + 'events_sell.csv', sell_headers)

events_swap = loadEvents("Swap", 1000, marketplace)
print("Events swap loaded!")
write_events_to_csv(events_swap, output_dir + 'events_swap.csv', swap_headers)

events_day_mint = loadEvents("Day_Mint", 1000, marketplace)
print("Events day_mint loaded!")
write_events_to_csv(events_day_mint, output_dir + 'events_day_mint.csv', day_mint_headers)

events_mint = loadEvents("Mint", 1000, paycoin)
print("Events mint loaded!")
write_events_to_csv(events_mint, output_dir + 'events_mint.csv', mint_headers)

print("Events successfully written to CSV files.")