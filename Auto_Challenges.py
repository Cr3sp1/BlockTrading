import asyncio
from brownie import accounts, network, exceptions, Contract, project, web3
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Challenge

print("Connecting to server...")
network.connect('development')
print("Connection successful!")


# Your address
account = str("0x0063046686E46Dc6F15918b61AE2B121458534a5")

# Address of the deployed Challenge contract
with open(brownie_dir + '/challenge_addr.txt', 'r') as challenge_addr_f:

			challenge_addr = str(challenge_addr_f.readline().strip('\n'))
			challenge = Challenge.at(challenge_addr)

# Sleep time 
sleep_time = 20

async def ovo_handle(event) -> None:

    challenge_index = event["args"]["index"]
    print(f"Processing One_vs_One event for challenge index {challenge_index}")
    await asyncio.sleep(20)  # Wait for the required 20 seconds
    try:
        tx = challenge.win_one(challenge_index, {'from': account})
        if( tx.return_value):
            print(f"Challenge {challenge_index} won!")
        else:
             print(f"Challenge {challenge_index} lost!")
    except Exception as e:
        print(f"Failed to answer One_vs_One challenge index {challenge_index}: {e}")


async def ovt_handle(event) -> None:

    challenge_index = event["args"]["index"]
    print(f"Processing One_vs_Two event for challenge index {challenge_index}")

    await asyncio.sleep(sleep_time)  # Wait for the required 20 seconds
    try:
        
        tx = challenge.win_two(challenge_index, {'from': account})
        if( tx.return_value):
            print(f"Challenge {challenge_index} won!")
        else:
             print(f"Challenge {challenge_index} lost!")

        print(f"Answered challenge index {challenge_index} for One_vs_Two")
    except Exception as e:
        print(f"Failed to answer One_vs_Two challenge index {challenge_index}: {e}")


async def main():
    print("Starting to listen for Challenge events...")

    processed_ids = []

    while True:

        block_num = web3.eth.block_number
        events_ovo = challenge.events.get_sequence(from_block=block_num - 5, to_block=block_num, event_type="One_vs_One")
        events_ovt = challenge.events.get_sequence(from_block=block_num - 5, to_block=block_num, event_type="One_vs_Two")
        
        try:

            for event in events_ovo:
                
                idx = event["args"]["index"]

                if idx not in processed_ids:
                    processed_ids.append(idx)
                    asyncio.create_task(ovo_handle(event))

            for event in events_ovt:

                idx = event["args"]["index"]

                if idx not in processed_ids:
                    processed_ids.append(idx)
                    asyncio.create_task(ovt_handle(event))

        except Exception as e:
            print(e)
        await asyncio.sleep(0.5)


asyncio.run(main())