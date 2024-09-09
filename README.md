# CryptoHedger
#### Video Demo:  https://www.youtube.com/watch?v=H_Gwg1esxko
#### Description: An experimental crypto hedging algorithm for perpetual futures on the Bitget exchange cross-margin USDT-M Futures.



		  /$$$$$$                              /$$             /$$   /$$               /$$
		 /$$__  $$                            | $$            | $$  | $$              | $$
		| $$  \__/ /$$$$$$ /$$   /$$ /$$$$$$ /$$$$$$   /$$$$$$| $$  | $$ /$$$$$$  /$$$$$$$ /$$$$$$  /$$$$$$  /$$$$$$
		| $$      /$$__  $| $$  | $$/$$__  $|_  $$_/  /$$__  $| $$$$$$$$/$$__  $$/$$__  $$/$$__  $$/$$__  $$/$$__  $$
		| $$     | $$  \__| $$  | $| $$  \ $$ | $$   | $$  \ $| $$__  $| $$$$$$$| $$  | $| $$  \ $| $$$$$$$| $$  \__/
		| $$    $| $$     | $$  | $| $$  | $$ | $$ /$| $$  | $| $$  | $| $$_____| $$  | $| $$  | $| $$_____| $$
		|  $$$$$$| $$     |  $$$$$$| $$$$$$$/ |  $$$$|  $$$$$$| $$  | $|  $$$$$$|  $$$$$$|  $$$$$$|  $$$$$$| $$
		 \______/|__/      \____  $| $$____/   \___/  \______/|__/  |__/\_______/\_______/\____  $$\_______|__/
		                   /$$  | $| $$                                                   /$$  \ $$
		                  |  $$$$$$| $$                                                  |  $$$$$$/
		                   \______/|__/                                                   \______/




# DISCLAIMER

CryptoHedger is an open-source experimental software, and the author does not take any responsibility for its usage. Users should understand the following:

Cryptocurrency trading carries inherent risks, and users should only engage with funds they can afford to lose. CryptoHedger does not provide financial advice, and users should seek guidance from a qualified financial advisor before trading.

Users are solely responsible for managing their risk exposure while using CryptoHedger. This includes implementing appropriate risk management strategies and choosing proper algorithm settings and position sizing.

The author of CryptoHedger is not liable for any damages or losses resulting from the use of the software. Users are expected to comply with all applicable laws and regulations governing cryptocurrency trading in their respective jurisdictions.

By using CryptoHedger, users acknowledge and accept these terms and agree to use the software at their own risk.



# WHAT IS CRYPTOHEDGER?

CryptoHedger is an open-source experimental algorithm designed based on a hedging mathematical model which balances long and short positions to ensure that gains consistently outweigh losses. Here's a good video explanation by EcoEngineering (https://www.youtube.com/watch?v=NGBPq_CSha8) which explains the mathematical model in detail, or scroll to the "How the algorithm works" section for a quicker explanation.

CryptoHedger only works on USDT-M cross margin perpetual futures with a minimum balance of 6 USDT.



# SYSTEM REQUIREMENTS

## Hardware

While minimum system specifications may vary depending on the underlying operating system, a very important requirement is a fast and stable internet connection, as this affects slippage and therefore profit.
Probably, the best solution is running CryptoHedger on a VPS.


## Software:

CryptoHedger depends on the 'CCXT' and 'requests' Python libraries. You can install these by typing the following commands in the terminal:

### to install 'CCXT':
	pip install ccxt

### to install 'requests':
	pip install requests

### Or, to install them altogether:
	pip install -r requirements.txt



# HOW TO LOGIN

First, you'll need a Bitget API with read-write futures orders permission. Please refer to Bitget's documentation on how to do that. Once done, you'll have an API key, a secret key, and a passphrase.
There are two ways to log in, one public and one private.


## Public login

Public login should only be used on your private machine or VPS, and it consists of pasting the API key, secret key, and passphrase in the corresponding text files already present in the "login_credentials" folder. CryptoHedger will read these and log in without any user input.

It's useful because it makes it easy to restart the software without having to paste API credentials multiple times, but I cannot stress enough the importance of keeping these private.

In a few words, USE WITH CAUTION.


## Private login

Private login simply consists of keeping the login text files in the "login_credentials" folder empty. In this way, upon starting CryptoHedger, you'll be prompted for the API credentials, without storing these on disk.
For extra security, you'll not see any character typed or pasted into the API credentials prompts (not even asterisks), so keep this in mind when logging in.



# INPUTS

## Base coin

After logging in, you'll be prompted for the base coin input. Remember, the only tradable coins are those in the USDT-M futures with no expiry (perpetual). The input is case-insensitive.
Type 'list all' to list all available coins in alphabetical order, or the partial name of a coin for suggestions.


## Algorithm inputs

These inputs are prompted after entering the menu choice '1. Start Hedger' (to start the algorithm) or '2. Batch Tester' (explained later).

- **Leverage:** Choose your leverage, between 1 and the maximum leverage of the chosen coin.

- **Initial percentage of margin (margin%):** The size of the initial position size as a percentage of margin (calculated as balance*leverage). It's highly advisable to keep this below 1% as it will exponentially increase at every step.
	The minimum trade size is 6 USDT; if margin% is lower, the minimum trade size will be applied instead.

- **Open level percent (open%):** Based on the starting price (RefPrice), it is used to calculate the prices at which to open long and short positions.
	These are calculated as (RefPrice+(open% of RefPrice)) for the long open price and (RefPrice-(open% of RefPrice)) for the short open price.

- **Close level percent (close%):** Based on the open level percent (open%), it is the price at which the series of positions (batch) is closed, and the algorithm starts from scratch (reset).
	It is calculated as (OpenLongPrice+(close% of RefPrice)) for the upper close price and (OpenShortPrice-(close% of RefPrice)) for the lower close price.

- **Multiplier:** The rate at which the position size is multiplied at every step.



# HOW THE ALGORITHM WORKS

This hedging mathematical model opens positions in opposite directions so that, with the proper settings, the profit from winning trades is always greater than the losses from losing trades and fees.
Have a look at the video explanation by EcoEngineering here --> https://www.youtube.com/watch?v=NGBPq_CSha8

Upon starting the algorithm, the first calculation is RefPrice, which is simply calculated from the ask and bid: (ask+bid)/2. It can be considered the starting current price that will be used to calculate the other four price levels,
listed below in order of value in the same way you'd see them on a trading chart:

UpperClosePrice = CLOSE ALL positions
OpenLongPrice = the price at which LONG positions are OPEN
RefPrice = starting current price
OpenShortPrice = the price at which SHORT positions are OPEN
LowerClosePrice = CLOSE ALL positions

The algorithm opens a series of trades at the open prices until one of the close prices is hit. A series of trades is called a BATCH.

It works in the following way:
The first trade size is the chosen percentage of margin (margin%), and it is opened when the price hits OpenLongPrice (opening a long position) or OpenShortPrice (opening a short position).

The subsequent trades are opened based on open positions and the Multiplier:
- A LONG POSITION is opened at OpenLongPrice if the value of short positions is greater than the value of long positions.
	The trade size is calculated as (ShortPositionsValue*Multiplier)-LongPositionsValue.

- A SHORT POSITION is opened at OpenShortPrice if the value of long positions is greater than the value of short positions.
	The trade size is calculated as (LongPositionsValue*Multiplier)-ShortPositionsValue.

All trades are closed either at UpperClosePrice or LowerClosePrice:
- At UpperClosePrice, the value of long positions should be greater than the value of short positions.

- At LowerClosePrice, the value of short positions should be greater than the value of long positions.

Therefore, provided that the algorithm is set up properly, the batch of trades should be overall profitable on either side. After that, the algorithm resets and starts again with a new batch based on the new current ask and bid prices.
REMEMBER: The winning trades should also cover platform fees, which are higher considering CryptoHedger uses only market orders, for now.


### From the terminal, a batch looks like this:

	RESET:: Time (UTC): 11:57 - 06/05/2024
	  ALGO LEVELS::  Ref price: 0.46519 - Open Long: 0.46565 - Open Short: 0.46472 - Close Long: 0.46798 - Close Short: 0.46239
	ACCOUNT:: Balance: 21.25 USDT - Margin: 1593.9 USDT
	OPEN SHORT:: Value: 6 USDT - Size: 13.0 ADA
	  Total positions: 6.0 USDT - Long: 0.0 USDT - Short: 6.0 USDT
	OPEN LONG:: Value: 18.0 USDT - Size: 39.0 ADA
	  Total positions: 24.0 USDT - Long: 18.0 USDT - Short: 6.0 USDT
	OPEN SHORT:: Value: 48.0 USDT - Size: 103.0 ADA
	  Total positions: 72.0 USDT - Long: 18.0 USDT - Short: 54.0 USDT
	Ask: 0.46235 - Bid: 0.4622
	12:22 - 06/05/2024 - BATCH END:: Profit: 0.04 USDT (0.19%)


## Algorithm issues [IMPORTANT]

Even with a minimal initial position size and the highes possible leverage (125X at the moment of writing) the position size grows exponentially, especially whith a tight open%.
When the account runs out of money, CryptoHedger closes the algorithm at one of the OpenPrice levels and most likely the losses will outgrow the wins. Use the Calculator.xlsx with your own settings to have an idea of your risk of running out of money.

**THIS IS AN EXPERIMENTAL ALGORITHM AND YOU ARE LIKELY TO LOSE MONEY WITH IT.**


# BATCH TESTING

The menu entry '2. Batch Tester' is not much different from '1. Start Hedger': it is, in fact, the same live trading function, but it stops after one batch and is made with the sole purpose of testing settings live without wasting too much budget.

At the end of the batch, you'll be prompted with the option to repeat the test with the same settings or to go back to the menu.



# SYMBOL SPECS

The menu entry '3. Symbol Specs' does nothing more than printing the API response while fetching the coin information from the Bitget API.
