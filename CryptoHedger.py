import ccxt
from difflib import get_close_matches
import getpass
import os
import requests
from datetime import datetime, timezone


def account_init():
    ...


def live_strategy_caller():
    ...


def algo_settings_input():
    ...


def hedger():
    ...


def login():
    ...


def num_input(input_message="", err_message="", min_value=0):
    ...


def open_long_live():
    ...


def open_short_live():
    ...


def print_logo():
    ...


def print_symbol_specs():
    ...


def reset():
    ...


def select_symbol():
    ...


# Initial Variables
bitget = None
symbol = ""
quote = "USDT"
volume_digits = 0
symbol_specs = {}
ask = 0.0
bid = 0.0
batch_tester = False

# Algo settings
account = {"balance": 0, "margin": 0, "leverage": 0, "min_trade": 0}
algo_inputs = {"open%": 0.0, "close%": 0.0, "multiplier": 0.0,
               "margin%": 0.0, "base_position_value": 0.0}
position_size = {"long": 0.0, "short": 0.0}
algo_var = {"refprice": 0.0, "openlong": 0.0, "openshort": 0.0, "closelong": 0.0, "closeshort": 0.0}

# MAIN FUNTION


def main():
    global bitget, symbol, quote, symbol_specs, batch_tester
    global account  # = {"balance": 0, "margin": 0, "leverage": 0, "min_trade": 0}

    # Print logo
    print_logo()

    # Connect
    while bitget is None:
        print("Connecting to Bitget exchange...")
        bitget = login()

    # Select symbol
    symbol = select_symbol()

    if account_init() == False:
        return

    # Print Menu
    while True:
        menu_input = input(
            "\n\n--- MENU ---\n\n 1. Start Hedger\n 2. Batch Tester\n 3. Symbol Specs\n 0. Exit\n")

        if menu_input == "1":
            print("Selected: Start Hedger\n")
            if algo_settings_input() == True:
                live_strategy_caller()
            continue

        elif menu_input == "2":
            print("Selected: Batch Tester\n")
            batch_tester = True
            if algo_settings_input() == True:
                live_strategy_caller()
            while True:
                user_input = input("\nDo you want to restest with same settings? y/n\n")
                if user_input == "y":
                    print("Restarting batch tester...")
                    live_strategy_caller()
                    continue
                elif user_input == "n":
                    batch_tester = False
                    break
                else:
                    print("Wrong answer! Only reply with y/n")
            continue

        elif menu_input == "3":
            print("Selected: Symbol Specs\n")

            print_symbol_specs()
            continue

        elif menu_input == "0":
            print("Selected: Exit\nProgram closed by user")
            return

        else:
            print("Invalid input!")


### INITIAL FUNCTIONS ###
# Print logo
def print_logo():
    logo_path = os.path.join(os.path.dirname(__file__), "logo")

    # Open and print logo file
    try:
        with open(logo_path, "r") as logo_file:
            print(logo_file.read())
    except:
        print("Logo missing!\n")

    return


# LOGIN FUNCTION
def login():
    global bitget
    global account  # = {"balance": 0, "margin": 0, "leverage": 0, "min_trade": 0}
    apikey = ""
    secretkey = ""
    password = ""

    # Account credentials from files
    apikey_path = os.path.join(os.path.dirname(__file__), "login_credentials/apikey.txt")
    secretkey_path = os.path.join(os.path.dirname(__file__), "login_credentials/secret_key.txt")
    password_path = os.path.join(os.path.dirname(__file__), "login_credentials/password.txt")

    with open(apikey_path, "r") as apikey_file:
        apikey = apikey_file.read().strip()

    with open(secretkey_path, "r") as secretkey_file:
        secretkey = secretkey_file.read().strip()

    with open(password_path, "r") as password_file:
        password = password_file.read().strip()

    # If login not stored on file
    if apikey == "":
        apikey = getpass.getpass("Enter API key (characters will not show): ")

    if secretkey == "":
        secretkey = getpass.getpass("Enter SecretKey (characters will not show): ")

    if password == "":
        password = getpass.getpass("Enter API passphrase (characters will not show): ")

    # Connection
    try:
        bitget = ccxt.bitget({
            'apiKey': apikey,
            'secret': secretkey,
            'password': password,
            'nonce': ccxt.bitget.milliseconds()
        })

    except ccxt.BaseError as e:
        print("Connection failed. Check:\n - API key\n - Secret key\n - API passphrase")
        print(e)
        return None

    if not bitget.fetchBalance():
        print("Connection failed. Check:\n - API key\n - Secret key\n - API passphrase")
        return None

    print("Connection successful")

    # Download symbols
    if bitget.load_markets():
        print("Symbols downloaded")
    else:
        print("Failed to download symbols")

    return bitget


# SYMBOL SELECTOR FUNCTION
def select_symbol():
    global symbol, quote
    assett_list = {}  # keys = base coins, values = symbols

    while len(assett_list) == 0:
        # Filter active linear futures swap symbols with no expiry and USDT as quote (USDT-M futures)
        for row in bitget.symbols:
            sym = bitget.market(row)
            if sym['active'] == True and sym['type'] == 'swap' and sym['settle'] == quote and sym['linear'] == True and sym['expiry'] == None:
                assett_list[sym['base']] = sym['symbol']

        if len(assett_list) > 0:
            print(len(assett_list), " symbols available\n")
        else:
            print("No symbols available, check your credentials")
            return

    # Select assett to trade
    while True:
        base = input("Search base coin:\n(type 'list all' for full list)\n")

        base = base.upper()
        if base == 'LIST ALL':
            for row in assett_list:
                print(row)
            continue

        if base in assett_list.keys():
            print("\nCoin selected:", base, "\nSymbol:", assett_list[base])
            return assett_list[base]

        matches = get_close_matches(base, assett_list.keys(), 100)
        if matches:
            print("Did you mean:", *matches, sep="\n")
        else:
            print("Symbol not found. Please try again.")
            matches = []

# Account data initializasion


def account_init():
    global bitget, volume_digits, symbol_specs
    global account  # = {"balance": 0, "margin": 0, "leverage": 0, "min_trade": 0}

    # Set cross margin mode
    try:
        bitget.setMarginMode('cross', symbol)
    except ccxt.BaseError as e:
        print("Error setting margin mode:", e, "\nCheck API settings")
        print(e)
        return False

    # Get balance and leverage
    symbol_specs = bitget.market(symbol)
    marginmode = bitget.fetchMarginMode(symbol)

    account['leverage'] = int(symbol_specs['info']['maxLever'])
    account['min_trade'] = int(symbol_specs['info']['minTradeUSDT']) + 1
    account['balance'] = float(marginmode['info']['crossedMaxAvailable'])
    volume_digits = int(symbol_specs['info']['volumePlace'])

    # Check account balance is at least 6 USDT
    print(" Max leverage:", str(account['leverage']) + "X\n",
          "Balance:", round(account['balance'], 2), quote)
    if account['balance'] < account['min_trade']:
        print("A minimum of", account['min_trade'], "USDT are needed, move at least", round(
            account['min_trade'] - account['balance'], 2), "USDT into the USDT-M futures account\nProgram closed for insufficient funds")
        return False

    return True

# Print symbol specs


def print_symbol_specs():
    global symbol_specs

    print("\n --- SYMBOL SPECS ---\n")

    for key, value in symbol_specs.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for inner_key, inner_value in value.items():
                print(f"  {inner_key}: {inner_value}")
        else:
            print(f"{key}: {value}")

    print("\n --- END ---\n")

    return

### ALGO FUNCTIONS ###
# NUMERICAL USER INPUT


def num_input(input_message="", error_message="", min_value=0, rounding=2):
    while True:
        user_input = input(input_message)
        try:
            user_input = float(user_input)
            if user_input >= min_value:
                return round(float(user_input), rounding)
            else:
                print(error_message)
                continue
        except:
            print(error_message)

# ALGO SETTINGS INPUTS


def algo_settings_input():
    global bitget, quote, account, algo_inputs

    print("\n--- ALGO SETTINGS ---\n")

    # Leverage user input
    max_leverage = int(symbol_specs['info']['maxLever'])
    while True:
        leverage_input = input(
            "Enter leverage (must be an integer between 1 and " + str(max_leverage) + ")\n")
        try:
            leverage_input = int(leverage_input)
            if leverage_input >= 1 and leverage_input <= max_leverage:
                account['leverage'] = int(leverage_input)

                try:
                    bitget.setLeverage(leverage_input, symbol)
                except ccxt.BaseError as e:
                    print(e)
                    print("\nUnable to set leverage, please try again")
                    continue

                account['margin'] = round(account['balance'] * account['leverage'], 2)
                print("Available margin:", account['margin'], quote)
                break
            else:
                print("Invalid! Must be an integer between 1 and)", account['leverage'])
                continue
        except:
            print("Invalid! Must be an integer between 1 and)", account['leverage'])

    # Margin percent user input
    min_margin_percent = round((account['min_trade']/account['margin'])*100, 2)

    algo_inputs["margin%"] = num_input("\nEnter initial percentage of margin \n(will be rounded to one decimal, must be >= 0.1%)\nMinimum buy is " + str(min_margin_percent) + "% of total margin, if lower minimum buy will be applied\n",
                                       "Invalid! Must be a number >= 0.1", 0.1, 1)
    # Open percent user input
    algo_inputs["open%"] = num_input("\nEnter open level percent, based on actual price\n(will be rouned to 2 decimals, must be >= 0.05%)\n",
                                     "Invalid! Must be a number >= 0.05", 0.05, 2)
    # Close percent user input
    algo_inputs["close%"] = num_input("\nEnter close level percent, based on open price\n(will be rouned to 2 decimals, must be >= 0.01%)\n",
                                      "Invalid! Must be a number >= 0.01", 0.01, 2)
    # Position multiplier user input
    algo_inputs["multiplier"] = num_input("\nEnter position multiplier\n(will be rouned to 1 decimal, must be >= 1.1)\n",
                                          "Invalid! Must be a number >= 1.1", 1.1, 1)

    print("\nALGO SETTINGS RECAP:\nLeverage:", str(account['leverage']) + "X\nMargin:", account['margin'], quote, "\nMargin percent:", str(
        algo_inputs['margin%']) + "%\nOpen percent:", str(algo_inputs['open%']) + "%\nClose percent:", str(algo_inputs['close%']) + "%\nMultiplier: ", algo_inputs['multiplier'], "\n")

    # Confirmation
    while True:
        confirmation_input = input("Do you want to start the hedging algorithm? y/n\n")

        if confirmation_input == "y":
            print("\nStarting algorithm...")
            return True
        elif confirmation_input == "n":
            print("\nAlgorithm initializtion aborted by user")
            return False
        else:
            print("Invalid! Only respond with 'y' for YES or 'n' for NO")
            continue

# MAIN LIVE ALGO FUNCTION


def live_strategy_caller():
    # Global variables
    global ask, bid, algo_var, account, algo_inputs, position_size

    # Initial hedger parameters calculation
    response = requests.get(
        "https://api.bitget.com/api/v2/mix/market/ticker?productType=USDT-FUTURES&symbol="+symbol_specs['id']).json()
    ask = float(response['data'][0]['askPr'])
    bid = float(response['data'][0]['bidPr'])

    if reset() == True:
        print("\n--- ALGORITHM STARTED ---\n")

        # Strategy caller
        while hedger() == True:
            try:
                response = requests.get(
                    "https://api.bitget.com/api/v2/mix/market/ticker?productType=USDT-FUTURES&symbol="+symbol_specs['id']).json()
            except ccxt.BaseError:
                print("--- ERROR: UNABLE TO FETCH TICKER, TRYING AGAIN")
                continue
            ask = float(response['data'][0]['askPr'])
            bid = float(response['data'][0]['bidPr'])

            print("Ask:", ask, "- Bid:", bid, "                   ", end="\r")

    print("Algorithm closed")
    return

# STRATEGY FUNCTION


def hedger():
    # Algo settings
    global ask, bid, algo_var, algo_inputs, position_size

    if bid >= algo_var["closelong"] or ask <= algo_var["closeshort"]:
        return reset()
    elif position_size["long"] <= position_size["short"] and (ask >= algo_var["openlong"] or bid >= algo_var["openlong"]):
        return open_long_live()
    elif position_size["short"] <= position_size["long"] and (ask <= algo_var["openshort"] or bid <= algo_var["openshort"]):
        return open_short_live()

    return True

# OPEN LONG POSITION FUNCTION


def open_long_live():
    # Global variables
    global symbol, quote, symbol_specs, volume_digits, ask, bid, account, algo_inputs, position_size

    # Position size calculation
    if position_size['long'] == 0 and position_size['short'] == 0:
        value = max(account['min_trade'], algo_inputs['base_position_value'])
    elif position_size['long'] < position_size['short']:
        value = (position_size['short'] * algo_inputs['multiplier']) - position_size['long']
        value = max(value, account['min_trade'])
    else:
        print("Internal error while calculating long position size")
        return False

    # Check margin availability and update margin
    if value <= account['margin']:
        value = round(value, volume_digits)
        account['margin'] -= value
        size = value/ask
        size = round(size, volume_digits)
    else:
        print("--- NOT ENOUGH MARGIN, ALGORITHM STOPPED ---")
        reset()
        return False

    # Open long position

    try:
        bitget.createOrder(symbol, 'market', 'buy', size)
    except ccxt.BaseError as e:
        print("--- ERROR: OPEN LONG FAILED - Value:", value,
              quote, "- Size:", size, symbol_specs['base'])
        print(e)
        return False

    print("OPEN LONG:: Value:", value, quote, "- Size:", size, symbol_specs['base'])
    position_size['long'] += value
    print("  Total positions:", position_size['long'] + position_size['short'], quote, "- Long:",
          position_size['long'], quote, "- Short:", position_size['short'], quote)

    return True

# OPEN LONG POSITION FUNCTION


def open_short_live():
    # Global variables
    global symbol, quote, symbol_specs, volume_digits, ask, bid, account, algo_inputs, position_size

    # Position size calculation
    if position_size['long'] == 0 and position_size['short'] == 0:
        value = max(account['min_trade'], algo_inputs['base_position_value'])
    elif position_size['long'] > position_size['short']:
        value = (position_size['long'] * algo_inputs['multiplier']) - position_size['short']
        value = max(value, account['min_trade'])
    else:
        print("Internal error while calculating short position size")
        return False

    # Check margin availability and update margin
    if value <= account['margin']:
        value = round(value, volume_digits)
        account['margin'] -= value
        size = value/bid
        size = round(size, volume_digits)
    else:
        print("--- NOT ENOUGH MARGIN, ALGORITHM STOPPED ---")
        reset()
        return False

    # Open short position
    try:
        bitget.createOrder(symbol, 'market', 'sell', size)
    except ccxt.BaseError as e:
        print("--- ERROR: OPEN SHORT FAILED - Value:", value,
              quote, "- Size:", size, symbol_specs['base'])
        print(e)
        return False

    print("OPEN SHORT:: Value:", value, quote, "- Size:", size, symbol_specs['base'])
    position_size['short'] += value
    print("  Total positions:", position_size['long'] + position_size['short'], quote, "- Long:",
          position_size['long'], quote, "- Short:", position_size['short'], quote)

    return True

# CLOSES ALL POSITIONS AND RESETS STRATEGY SETTINGS


def reset():
    # Global variables
    global symbol, symbol_specs, batch_tester, ask, bid, algo_var, volume_digits, account, algo_inputs, position_size

    # Close all positions
    while len(bitget.fetchPosition(symbol)['info']) != 0:
        if position_size['long'] != 0 or position_size['short'] != 0:
            try:
                bitget.closeAllPositions(
                    params={'symbol': symbol_specs['id'], 'productType': 'USDT-FUTURES'})
            except ccxt.BaseError as e:
                print(e)
                print("--- ERROR: UNABLE TO CLOSE POSITIONS, TRYING AGAIN")
                continue

    # Update account info
    marginmode = bitget.fetchMarginMode(symbol)
    prev_balance = account['balance']
    account['balance'] = float(marginmode['info']['crossedMaxAvailable'])
    account['margin'] = round(account['balance'] * account['leverage'], 2)
    algo_inputs["base_position_value"] = (account['margin']/100) * algo_inputs['margin%']
    algo_inputs["base_position_value"] = max(
        algo_inputs["base_position_value"], account['min_trade'])
    algo_inputs["base_position_value"] = round(algo_inputs["base_position_value"], volume_digits)
    profit = account["balance"] - prev_balance
    profit_percent = profit/(prev_balance/100)

    # Print profit if is not a reset
    if profit != 0:
        print()
        print(datetime.now(timezone.utc).strftime('%H:%M - %d/%m/%Y'), "- BATCH END:: Profit:",
              round(profit, 2), quote, "(" + str(round(profit_percent, 2)) + "%)")

    # Reset calculations
    temp_symbol_data = bitget.fetchTicker(symbol)
    ask = float(temp_symbol_data['ask'])
    bid = float(temp_symbol_data['bid'])
    price_digits = int(symbol_specs['info']['pricePlace'])
    ref_price = (ask + bid) / 2
    open_partial = (algo_inputs["open%"] * ref_price) / 100
    close_partial = (algo_inputs["close%"] * ref_price) / 100

    # Reset algo values
    algo_var["refprice"] = round(ref_price, price_digits)
    algo_var["openlong"] = round(ref_price + open_partial, price_digits)
    algo_var["openshort"] = round(ref_price - open_partial, price_digits)
    algo_var["closelong"] = round(algo_var["openlong"] + close_partial, price_digits)
    algo_var["closeshort"] = round(algo_var["openshort"] - close_partial, price_digits)
    position_size["long"] = 0.0
    position_size["short"] = 0.0

    # Batch Tester handler
    if batch_tester == True and profit != 0:
        print("\n--- END TEST ---\n")
        return False

    print("\nRESET:: Time (UTC):", datetime.now(timezone.utc).strftime('%H:%M - %d/%m/%Y'), "\n  ALGO LEVELS:: ", "Ref price:", algo_var['refprice'], "- Open Long:", algo_var['openlong'], "- Open Short:",
          algo_var['openshort'], "- Close Long:", algo_var['closelong'], "- Close Short:", algo_var['closeshort'],
          "\nACCOUNT:: Balance:", round(account["balance"], 2), quote, "- Margin:", account["margin"], quote)

    return True


if __name__ == "__main__":
    main()
