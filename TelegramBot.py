import logging
import binascii
import functools
import re
import json

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from web3.exceptions import BadResponseFormat
from brownie import accounts, network, exceptions, Contract, project
brownie_dir = './Brownie/'
p = project.load(brownie_dir, name="DEXProject")
p.load_config()
from brownie.project.DEXProject import Token, Marketplace
network.connect('development')
#network.connect('ganache-local')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TASK, DATA, TYPE, INT_ACT, EXT_ACT, SECOND_SEL, TRADE, TRADE_SWAP, TRADE_FINALIZE, INT_FINALIZE, INT_CONFIRM, END = range(12)
KEY_SAVE = range(1)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if not await check_regitration(update):
        return ConversationHandler.END

    reply_keyboard = [["monitor"],["market"]]

    await update.message.reply_text(
        "Do you want to monitor the actual status or to make some actions on the market?", 
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select an action type."
        )
    )

    return TASK

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
        "Bot usage: \n" +
        "/set_account Used to set your private keys. \n" +
        "/start Starts the conversation with bot. \n" + 
        "/balance View your current balance. \n" +
        "/trade Open the trading window. \n" + 
        "/cancel Cancel all the current actions. ",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    #Stores the selected task and respond accordingly
    logger.info("Task requested: %s", update.message.text)

    reply_keyboard = []
    reply_text = ""
    return_state = 0

    match update.message.text:

        case "monitor":

            reply_keyboard = [["balance"], ["price"],["quantity"]]
            reply_text = "What variable do you want to monitor?"
            return_state = DATA
        
        case "market":

            reply_keyboard = [["external"],["internal"]]
            reply_text = "Do you want to perform an operation internal or external from your pool?"
            return_state = TYPE

    await update.message.reply_text(
        reply_text, 
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select an action type."
        )
    )

    return return_state

async def data(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd_shortcut = None) -> int:

    if not await check_regitration(update):
        return ConversationHandler.END

    in_data = update.message.text
    user = update.message.from_user.id

    if cmd_shortcut != None:
        in_data = cmd_shortcut

    match in_data:

        case "balance": 

            balances = [token.balanceOf(registered_accounts[user][0].address, {'from': registered_accounts[user][0]}) / 1e18 for token in token_list]

            await update.message.reply_text(
                "You current balance is: \nPC: {}\n".format(balances[0]) +
                "\n".join(["{}: {}".format(token_symbols[idx], balance) for idx, balance in enumerate(balances[1:])]),
                reply_markup=ReplyKeyboardRemove()
            )

        case "price":
            
            prices = []

            for idx, token in enumerate(token_list[1:]):

                prices.append(token_symbols[idx] + ": " + str(market.price(token.address, {'from': registered_accounts[user][0]}) / 1e18) + "PC")
            
            await update.message.reply_text(    
                "The current token prices are: \n" + "\n".join(prices),
                reply_markup=ReplyKeyboardRemove()
            )

        case "quantity":
            
            quantities = []

            for idx, token in enumerate(token_list[1:]):

                quantities.append(token_symbols[idx] + ": " + str(token.balanceOf(market.address, {'from': registered_accounts[user][0]}) / 1e18) + token_symbols[idx])

            await update.message.reply_text(    
                "The current tokens in the pool are: \n" + "\n".join(quantities),
                reply_markup=ReplyKeyboardRemove()
            )

    return ConversationHandler.END

async def type_sel(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd_shortcut = None) -> int:
    
    if not await check_regitration(update):
        return ConversationHandler.END

    #Stores the selected task and respond accordingly
    logger.info("Market type requested: %s", update.message.text)

    reply_keyboard = []
    reply_text = "Select the action you want to perform."
    return_state = 0

    in_text = update.message.text

    if cmd_shortcut != None:
        in_text = cmd_shortcut

    match in_text:

        case "external":

            reply_keyboard = [["buy"],["sell"],["swap"]]
            return_state = EXT_ACT
        
        case "internal":

            reply_keyboard = [["Increase Stake"],["Decrease Stake"]]
            return_state = INT_ACT

    await update.message.reply_text(
        reply_text, 
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select an action type."
        )
    )

    return return_state

async def int_act(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    #Stores the selected task and respond accordingly
    logger.info("Internal action requested: %s", update.message.text)

    context.user_data.update({'internal_act': update.message.text})

    await update.message.reply_text("Please select the amount of tokens you want to deposit/withdraw.")

    return INT_CONFIRM

async def int_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.from_user.id
    token_amount = float(update.message.text)
    owned_token_symbol = registered_accounts[update.message.from_user.id][1]
    owned_token_idx = token_symbols.index(owned_token_symbol) + 1
    paycoin_amount = market.price(token_list[owned_token_idx].address, {'from': registered_accounts[user][0]}) / 1e18 * token_amount

    await update.message.reply_text(
        "The operation will move {}PC and {}{}.\n".format(paycoin_amount, token_amount, owned_token_symbol) + 
        "Do you want to continue?",
        reply_markup=ReplyKeyboardMarkup(
            [["Yes"], ["No"]], one_time_keyboard=True, input_field_placeholder="Select an action type."
        )
    )

    context.user_data.update({"int_amount": token_amount})
    context.user_data.update({"int_pc_amount": paycoin_amount})
    context.user_data.update({"int_token_idx": owned_token_idx})

    return INT_FINALIZE

async def int_finalize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.from_user.id
    confirm_action = update.message.text

    try:

        match confirm_action:

            case "Yes":
                
                token_idx = context.user_data["int_token_idx"]
                token_amount = context.user_data["int_amount"]
                pc_amount = context.user_data["int_pc_amount"]
                user_account = registered_accounts[user][0]

                match context.user_data["internal_act"]:

                    case "Increase Stake":

                        token_list[0].increaseAllowance(pc_amount * 1e18, market.address, {'from': user_account})
                        token_list[token_idx].increaseAllowance(token_amount * 1e18, market.address, {'from': user_account})
                        market.mint_stake(token_list[token_idx], token_amount * 1e18, {'from': user_account})
                        
                    case  "Decrease Stake":

                        market.burn_stake(token_list[token_idx], token_amount * 1e18, {'from': user_account})

                await update.message.reply_text("Operation successful.", reply_markup=ReplyKeyboardRemove())

            case "No":

                await update.message.reply_text("Operation aborted.", reply_markup=ReplyKeyboardRemove())

    except BadResponseFormat as err:

        error = parse_bad_response(err)
        await update.message.reply_text(
            "Something went wrong, transaction reverted.\nError: " + error, 
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END

async def select_token(update: Update, second = False, full = False) -> None:

    reply_keyboard = []
    second_txt = ''

    if second:
        second_txt = "second "

    for symbol in token_symbols:

        if symbol != registered_accounts[update.message.from_user.id][1] or full:
            reply_keyboard.append([symbol])
        else:
            pass

    await update.message.reply_text(
        "Please select a {}token.".format(second_txt),
        reply_markup = ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Available tokens:"
        )
    )

async def second_sel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    requested_token = update.message.text
    token_idx = token_symbols.index(requested_token) + 1

    first_token_price = market.tokenToPaycoin(token_list[token_idx].address, 1e18)

    context.user_data.update({"token_idx": token_idx})
    context.user_data.update({"token_price": first_token_price})

    await select_token(update, True, True)

    return TRADE_SWAP

async def trade_swap(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.from_user.id
    requested_token = update.message.text
    first_token_idx = context.user_data["token_idx"]
    first_token_symbol = token_symbols[first_token_idx - 1]
    second_token_idx = token_symbols.index(requested_token) + 1

    first_token_price = context.user_data["token_price"]
    token_balance = token_list[first_token_idx].balanceOf(registered_accounts[user][0].address, {'from': registered_accounts[user][0]}) / 1e18
    swap_price = market.paycoinToToken(token_list[second_token_idx].address, first_token_price) / 1e18

    await update.message.reply_text(
        "The current price for 1{} is: {}{}\n".format(requested_token, swap_price, first_token_symbol) +
        "You currently have {}{}\n".format(token_balance, first_token_symbol) +
        "Please select the amount of {} you want to trade.\n".format(first_token_symbol),
    )

    context.user_data.update({"second_token_idx": second_token_idx})

    return TRADE_FINALIZE  

async def ext_act(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    #Stores the selected task and respond accordingly
    logger.info("External action requested: %s", update.message.text)
    return_state = ConversationHandler.END

    try:

        match update.message.text:

            case "swap":
                await select_token(update, False, True)
                context.user_data.update({"act": update.message.text})
                return_state = SECOND_SEL

            case _:
                await select_token(update)
                context.user_data.update({"act": update.message.text})
                return_state = TRADE

    except:
        await update.message.reply_text("Ooops, something went wrong!")

    # Handle external actions

    return return_state

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user = update.message.from_user.id
    requested_token = update.message.text
    token_idx = token_symbols.index(requested_token) + 1

    token_price = market.tokenToPaycoin(token_list[token_idx].address, 1e18, {'from': registered_accounts[user][0]}) / 1e18
    paycoin_balance = token_list[0].balanceOf(registered_accounts[user][0].address, {'from': registered_accounts[user][0]}) / 1e18
    token_balance = token_list[token_idx].balanceOf(registered_accounts[user][0].address, {'from': registered_accounts[user][0]}) / 1e18

    balance_str = str(paycoin_balance) + 'PC' if context.user_data["act"] == "buy" else str(token_balance) + token_symbols[token_idx - 1]

    await update.message.reply_text(
        "The current price for 1{} is: {}PC\n".format(requested_token, token_price) +
        "You currently have {}\n".format(balance_str) +
        "Please select the amount of {} you want to trade.\n".format(requested_token),
    )

    context.user_data.update({"token_idx": token_idx})
    context.user_data.update({"token_price": token_price})

    return TRADE_FINALIZE

async def finalize_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    amount = float(update.message.text)
    token_price = float(context.user_data["token_price"])
    pc_amount = amount * token_price
    token_idx = context.user_data["token_idx"]
    user = update.message.from_user.id
    user_account = registered_accounts[user][0]

    try:
        match context.user_data["act"]:

            case "buy":

                token_list[0].increaseAllowance(pc_amount * 1e18, market.address, {'from': user_account})
                market.buy(token_list[token_idx].address, pc_amount * 1e18, {'from': user_account})

            case "sell":

                token_list[token_idx].increaseAllowance(amount * 1e18, market.address, {'from': user_account})
                market.sell(token_list[token_idx].address, amount * 1e18 ,{'from': user_account})

            case "swap":

                second_token_idx = context.user_data["second_token_idx"]

                paycoin_amount = market.tokenToPaycoin(token_list[token_idx].address, amount * 1e18)

                token_list[token_idx].increaseAllowance(amount * 1e18, market.address, {'from': user_account})
                token_list[0].increaseAllowance(paycoin_amount, market.address, {'from': user_account})

                market.swap(token_list[token_idx].address, token_list[second_token_idx].address, amount * 1e18, {'from': user_account})

        await update.message.reply_text("Operation succesfull.", reply_markup=ReplyKeyboardRemove())

    except BadResponseFormat as err:

        error = parse_bad_response(err)
        await update.message.reply_text(
            "Something went wrong, transaction reverted.\nError: " + error, 
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END

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

async def check_regitration(update: Update) -> bool:

    if update.message.from_user.id not in registered_accounts:

        await update.message.reply_text(
            "You have to register using the /set_account command before using the bot!",
            reply_markup=ReplyKeyboardRemove()
        )

        return False
    
    return True

def main() -> None:

    # Init contracts
    load_contracts()

    global registered_accounts
    registered_accounts = dict()

    # Run the bot.
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7126980510:AAGDECNvBm0wYSrRm57Tmjk026dvva_3Dyg").build()

    conv_handler = ConversationHandler(

        entry_points=[
            
            CommandHandler("start", start), 
            CommandHandler("help", help),
            CommandHandler("trade", functools.partial(type_sel, cmd_shortcut = "external")),
            CommandHandler("balance", functools.partial(data, cmd_shortcut = "balance"))
            
        ],
        states={
        
            TASK: [MessageHandler(filters.Regex("^(monitor|market)$"), task)],
            DATA: [MessageHandler(filters.Regex("^(balance|price|quantity)$"), data)],
            TYPE: [MessageHandler(filters.Regex("^(external|internal)$"), type_sel)],
            INT_ACT: [MessageHandler(filters.Regex("^(Increase Stake|Decrease Stake)$"), int_act)],
            INT_CONFIRM: [MessageHandler(filters.Regex("^[+-]?([0-9]*[.])?[0-9]+$"), int_confirm)],
            INT_FINALIZE: [MessageHandler(filters.Regex("^(Yes|No)$"), int_finalize)],
            SECOND_SEL: [MessageHandler(filters.Regex("^({})$".format('|'.join(token_symbols))), second_sel)],
            EXT_ACT: [MessageHandler(filters.Regex("^(buy|sell|swap)$"), ext_act)],
            TRADE: [MessageHandler(filters.Regex("^({})$".format('|'.join(token_symbols))), trade)],
            TRADE_SWAP: [MessageHandler(filters.Regex("^({})$".format('|'.join(token_symbols))), trade_swap)],
            TRADE_FINALIZE: [MessageHandler(filters.Regex("^[+-]?([0-9]*[.])?[0-9]+$"), finalize_trade)],
            END: [MessageHandler(None, cancel)],

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
    application.add_handler(registration_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()