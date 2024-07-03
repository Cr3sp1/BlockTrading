import logging
import binascii
import re
import json
import csv
import asyncio
import nest_asyncio
nest_asyncio.apply()

from telegram import (
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove, 
    Update, 
    ForceReply, 
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from brownie import web3
from web3.exceptions import BadResponseFormat
from brownie import accounts, network, exceptions, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace, Challenge
network.connect('development')
#network.connect('ganache-local')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SELECT_TYPE, SELECT_TARGET, END = range(3)
KEY_SAVE = range(1)

# funzione che crea la challenge 1v1
def onev1( rival, challenger ):
    challenge.one_vs_one( rival, {'from': challenger} )

# funzione che crea la challenge 1v2
def onev2( rival1, rival2, challenger ):
    challenge.one_vs_two( rival1, rival2, {'from': challenger} )


# funzione che vince la challenge 1v1
def winv1( index, answerer ) -> bool:
    tx = challenge.win_one( index, {'from': answerer} )
    return tx.return_value


# funzione che crea la challenge 1v2
def winv2( index, answerer ) -> bool:
    tx = challenge.win_two( index, {'from': answerer} )
    return tx.return_value

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

def parse_bad_response(err: BadResponseFormat):
        
        json_err = json.loads(re.sub(r'^.*?\{', '{', str(err)).replace("'", '"'))
        return extract_values(json_err, "reason")[0]

async def launch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not await check_regitration(update):
        return ConversationHandler.END

    reply_keyboard = [["1v1"], ["1v2"]]

    await update.message.reply_text(
        "Select the challenge type.", 
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select an action type."
        )
    )

    return SELECT_TYPE

async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    response = update.message.text
    user_account = registered_accounts[update.message.from_user.id][0]
    user_key = user_account.address

    reply_keyboard = []
    other_owners = []

    for idx, token in enumerate(token_list[1:]):

        if user_key != token.owner({'from': user_account}):

            reply_keyboard.append([token_symbols[idx]])
            other_owners.append(token.owner({'from': user_account}))
                
    try: 

        match response:

            case "1v1":
                
                await update.message.reply_text(
                    "Select your opponent.",
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select a token owner."
                    )
                )

                return SELECT_TARGET

            case "1v2":
                
                onev2(other_owners[0], other_owners[1], user_account)

                await update.message.reply_text("Challenge launched!", reply_markup=ReplyKeyboardRemove())

    except BadResponseFormat as err:

        error = parse_bad_response(err)
        await application.bot.send_message(
            update.callback_query.from_user.id,
            error, 
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END

async def select_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_account = registered_accounts[update.message.from_user.id][0]
    target_sym = update.message.text
    owner_id = token_symbols.index(target_sym)

    target = token_owners[owner_id]
    onev1(target, user_account)

    await update.message.reply_text("Challenge launched!", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

async def ovo_handle(event) -> None:

    challenger = event["args"]["challenger"]
    rival = event["args"]["rival"]
    challenge_idx = event["args"]["index"]
    challenger_symbol = None
    rival_symbol = None

    for idx, owner in enumerate(token_owners):
        
        if challenger == owner:
            challenger_symbol = token_symbols[idx]

        if rival == owner:
            rival_symbol = token_symbols[idx]

    challenge_dict.update({challenge_idx: ["1v1", challenger_symbol, rival_symbol, None]})

    try:

        for user_id in list(registered_accounts.keys()):

            user_addr = registered_accounts[user_id][0].address

            if user_addr == rival or user_addr == challenger:

                await application.bot.send_message(
                    user_id, 
                    "1v1 challenge: \nYou have been challenged by {}!".format(challenger_symbol), 
                    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Answer", callback_data="a{}".format(challenge_idx))]])   
                )

    except Exception as e:

        await application.bot.send_message(
            user_id, 
            "Error: {}".format(e), 
            reply_markup = ReplyKeyboardRemove()
        )  

async def ovt_handle(event) -> None:

    challenger = event["args"]["challenger"]
    challenge_idx = event["args"]["index"]
    challenger_symbol = None

    for idx, owner in enumerate(token_owners):
        
        if challenger == owner:
            challenger_symbol = token_symbols[idx]

    challenge_dict.update({challenge_idx: ["1v2", challenger_symbol, "all", None]})

    try:

        for user_id in list(registered_accounts.keys()):

            await application.bot.send_message(
                user_id, 
                "1v2 challange: \n Anyone can win!", 
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Answer", callback_data="b{}".format(challenge_idx))]])   
            )

    except Exception as e:

        await application.bot.send_message(
            user_id, 
            "Error: {}".format(e), 
            reply_markup = ReplyKeyboardRemove()
        )  


async def answer_challenge_ovo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    query = update.callback_query
    idx = int(query.data[1:])
    user_symb = registered_accounts[update.callback_query.from_user.id][1]
    user = registered_accounts[update.callback_query.from_user.id][0]

    await query.answer()

    try:

        won = winv1(idx, user)

        if won:

            challenge_dict[idx][-1] = user_symb
            csv_writer.writerow(challenge_dict[idx])

            await application.bot.send_message(
                update.callback_query.from_user.id,
                "You won the challenge!",
                reply_markup=ReplyKeyboardRemove()
            )  

        else: 

            await application.bot.send_message(
                update.callback_query.from_user.id,
                "Too early!",
                reply_markup=ReplyKeyboardRemove()
            )  

    except BadResponseFormat as err:

        error = parse_bad_response(err)
        await application.bot.send_message(
            update.callback_query.from_user.id,
            error, 
            reply_markup=ReplyKeyboardRemove()
        )

async def answer_challenge_ovt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    query = update.callback_query
    idx = int(query.data[1:])
    user_symb = registered_accounts[update.callback_query.from_user.id][1]
    user = registered_accounts[update.callback_query.from_user.id][0]

    await query.answer()
    try:

        won = winv2(idx, user)

        if won:

            challenge_dict[idx][-1] = user_symb
            csv_writer.writerow(challenge_dict[idx])

            await application.bot.send_message(
                update.callback_query.from_user.id,
                "You won the challenge!",
                reply_markup=ReplyKeyboardRemove()
            )  

        else: 

            await application.bot.send_message(
                update.callback_query.from_user.id,
                "Too early!",
                reply_markup=ReplyKeyboardRemove()
            )  

    except BadResponseFormat as err:

        error = parse_bad_response(err)
        await application.bot.send_message(
            update.callback_query.from_user.id,
            error, 
            reply_markup=ReplyKeyboardRemove()
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def set_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user = update.effective_user
    user_id = user.id

    if user_id in registered_accounts:

        await update.message.reply_text("It seems that your account have already been registered!!")
        return ConversationHandler.END

    else: 

        await update.message.reply_html(
            "Welcome to the registration procedure, {}!\n".format(user.mention_html()) +
            "Please enter your private key to complete registration.",
            reply_markup = ForceReply(selective = True)
        )

    return KEY_SAVE

async def key_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.effective_user.id
    key = update.message.text

    try:

        new_account = accounts.add(key)

        try:
            
            token_idx = token_owners.index(new_account.address)
            registered_accounts.update({user: [new_account, token_symbols[token_idx]]})

            await update.message.reply_text(
                "Your account have been succesfully registered! You can now start the bot with /start"
            )

        except ValueError:
            
            accounts.remove(new_account)

            await update.message.reply_text(
                "What you have provided does not seem to be a token owner key!!\n"
                "Please restart the registration procedure."
            )

            return ConversationHandler.END

    except binascii.Error:
        await update.message.reply_text(
            "What you have provided does not seem to be a valid key!!\n"
            "Please restart the registration procedure."
        )

    return ConversationHandler.END

async def monitor_challenge():

    processed_ids = []

    while True:

        block_num = web3.eth.block_number
        events_ovo = challenge.events.get_sequence(from_block=block_num - 2, to_block=block_num, event_type="One_vs_One")
        events_ovt = challenge.events.get_sequence(from_block=block_num - 2, to_block=block_num, event_type="One_vs_Two")
        
        try:

            for event in events_ovo:
                
                idx = event["args"]["index"]

                if idx not in processed_ids:
                    processed_ids.append(idx)
                    await ovo_handle(event)

            for event in events_ovt:

                idx = event["args"]["index"]

                if idx not in processed_ids:
                    processed_ids.append(idx)
                    await ovt_handle(event)  

        except Exception as e:
            print(e)
        await asyncio.sleep(1)
            
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

async def check_regitration(update: Update) -> bool:

    if update.message.from_user.id not in registered_accounts:

        await update.message.reply_text(
            "You have to register using the /set_account command before using the bot!",
            reply_markup=ReplyKeyboardRemove()
        )

        return False
    
    return True

def init_bot() -> None:

    conv_handler = ConversationHandler(

        entry_points=[CommandHandler("launch", launch)],
        states={
        
            SELECT_TYPE: [MessageHandler(filters.Regex("^(1v1|1v2)$"), select_type)],
            SELECT_TARGET: [MessageHandler(filters.Regex("^({})$".format('|'.join(token_symbols))), select_target)],
            END: [MessageHandler(None, cancel)]

        },
        
        fallbacks=[CommandHandler("cancel", cancel)],
    
    )

    registration_handler = ConversationHandler(

        entry_points = [CommandHandler("set_account", set_account)],
        states = {

            KEY_SAVE: [MessageHandler(filters.Regex("^[a-z0-9]{66}$"), key_save)]

        },

        fallbacks=[CommandHandler("cancel", cancel)]

    )

    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(answer_challenge_ovo, pattern = "^a[0-9]+$"))
    application.add_handler(CallbackQueryHandler(answer_challenge_ovt, pattern = "^b[0-9]+$"))
    application.add_handler(registration_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def main() -> None:

    # Init contracts
    load_contracts()

    global registered_accounts
    global application
    global subscribe
    global challenge_log_f
    global csv_writer
    global challenge_dict

    challenge_log_f = open("challenge_log.csv", 'a')
    csv_writer = csv.writer(challenge_log_f, delimiter=',')
    subscribe = True
    registered_accounts = dict()
    challenge_dict = dict()

    # Run the bot.
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7070565723:AAEeITkN16YwP4-JQQ-Ei4kMKATj1rA7Wko").build()

    await asyncio.gather(
        asyncio.create_task(monitor_challenge()),
        asyncio.create_task(init_bot())
    )

if __name__ == "__main__":
    asyncio.run(main())
    challenge_log_f.close()