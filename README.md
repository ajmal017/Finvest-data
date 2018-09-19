# Finvest data from YahooFinance
Collects real-time intraday data from Global Financial markets. No API or registration reqired. The latest version includes pools of: Currencies, Commodities, Cryptocurrencies [TBD], World Indices [TBD], US Treasury Bonds Rates [TBD]. Fast, reliable, but limited to processing one pool at a time

# How it works?
1. Creates a directory DATA to store collected data in databases
2. User selects pool of securitues
3. Opens URL page, retrieves set of listed securities
4. Creates database to store timestamps, tickers, values
5. Prompts user for a time lag of retrieving data
6. Refreshes URL page, retrieves values of tickers, values
7. Writes data to database with timestamp
8. Displays retrieved data with intermediary reports

# version 0.95
- available pools: currencies, commodities
- optimized for better performance on weak machines
- automatically adapts to changes in datasets provided
