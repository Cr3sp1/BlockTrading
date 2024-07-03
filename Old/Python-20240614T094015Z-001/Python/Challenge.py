from brownie import network, Contract, accounts, web3
from brownie.network.event import _decode_logs
import json, time, telegram, asyncio

with open('/home/daniele_atzori/Blockchain/esame/abi/Challenge.json') as json_file:
	challenge_abi = json.load(json_file)
challenge = Contract.from_abi('Challenge', address='0x08dE443F923ceA4E7dDB35a37B552d4ae9Bf156f', abi= challenge_abi)

challenge = Contract('0x08dE443F923ceA4E7dDB35a37B552d4ae9Bf156f')
launched = {}
win = {}
bot = telegram.Bot('6149747391:AAHceZHCSrJn3j480cOXcARuoKB3_wbfGhs')


def launch_single_challenge(address):
	launched_log = challenge.one_vs_one(address,{'from': accounts[0]})
	launched = _decode_logs(launched_log.logs)
	f = open('data_challenge.txt', 'w')
	f.write(str(launched[0][0]['buyer']), end = ' ')
	f.write(str(launched[0][0]['value']/1e18))
	f.write('\n')
	f.close()

def launch_team_challenge(address_1, address_2):
	launched_log = challenge.one_vs_two(address_1, address_2, {'from': accounts[0]})
	launched = _decode_logs(launched_log.logs)
	print(launched)
	f = open('data_challenge.txt', 'w')
	f.write(str(launched[0][0]['buyer']), end = ' ')
	f.write(str(launched[0][0]['value']/1e18))
	f.write('\n')
	f.close()

async def monitor_challenge():
	while True:
		try:
			single_challenge_log = challenge.events.get_sequence(from_block = web3.eth.blockNumber - 2, to_block = web3.eth.blockNumber, event_type = "One_vs_One")
			rival = single_challenge_log[0]['args']['_rival']
			if(rival == accounts[0]):
				async with bot:
					await bot.send_message(text="You're challenged!!", chat_id=6150362686)
				time.sleep(60)
		except:
			try:
				team_challenge_log = challenge.events.get_sequence(from_block = web3.eth.blockNumber - 2, to_block = web3.eth.blockNumber, event_type = "One_vs_Two")
				rival_1 = team_challenge_log[0]['args']['_rival_1']
				rival_2 = team_challenge_log[0]['args']['_rival_2']
				if(rival_1 == accounts[0]) or (rival_2 == accounts[0]):
					async with bot:
						await bot.send_message(text="You're challenged!!", chat_id=6150362686)
					time.sleep(60)
			except:
				time.sleep(10)

def call_one():
	win_log = challenge.win_one({'from':accounts[0]})
	win = _decode_logs(win_log.logs)
	f = open('challenge_events.txt', 'w')
	f.write(str(win[0][0]['buyer']), end = ' ')
	f.write(str(win[0][0]['value']/1e18))
	f.write('\n')

def call_two():
	win_log = challenge.win_two({'from':accounts[0]})
	win = _decode_logs(win_log.logs)
	f = open('challenge_events.txt', 'w')
	f.write(str(win[0][0]['buyer']), end = ' ')
	f.write(str(win[0][0]['value']/1e18))
	f.write('\n')

if __name__ == '__monitor_challenge__':
	asyncio.run(monitor_challenge())
