# YFmarkets v0.95 pre-release
# by Oleksii Lialka

from urllib.request import urlopen
import urllib.error
from bs4 import BeautifulSoup
import re, os, ssl, sqlite3, string
from time import time, sleep, strftime
from datetime import date, datetime

#clear screen
def fn_clear():
    """
    Function takes no arguments.
    Clears screen.
    Returns none.
    """
    try: os.system('cls')
    except: os.system('clear')
    finally: pass
fn_clear()

# create data dir
if 'data' not in os.listdir():
    os.mkdir('data') ; os.chdir('data')
    print('Data directory created')
else:
    os.chdir('data')
    print('Data directory already exists')

# Main menu. Select tickers into a list
lst = ('currencies', 'commodities', 'crypto')

print('''
Available pools:
1. Currencies
2. Commodities
3. Cryptocurrencies [TBD]
4. World Indices [TBD]
5. US Treasury Bonds Rates [TBD]
-> Press "Ctrl+C" to quit''')

while True:
    opt = input('\nSelect a set of tickers: ')
    try:
        if len(opt) < 1:
            opt = 1
            url = 'https://finance.yahoo.com/currencies'
            break
        elif int(opt) == 1:
            opt = 1
            url = 'https://finance.yahoo.com/currencies'
            break
        elif int(opt) == 2:
            opt = 2
            url = 'https://finance.yahoo.com/commodities'
            break
    except:
        print('Invalid entry')
        continue

# Set interval of retrieving data. Default value - 0 sec
while True:
    lag_in = input('\nEnter data mining lag (seconds): ')
    try:
        if len(lag_in) < 1:
            lag = 0
            break
        else:
            lag = int(lag_in)
            break
    except:
        print('Invalid entry')
        continue

# Timeout for urlopen
t_out = 2

# URL opening
def fn_urlopen(url):
    """
    Function takes argument: url.
    Opens, parses web-page.
    Returns none.
    """
    global tags
    with urlopen(url, timeout = t_out) as page:
        html = page.read()
    soup = BeautifulSoup(html, "html.parser",from_encoding="iso-8859-1")
    tags = soup('td')

# Retrieve tickers
def fn_tickers(opt):
    """
    Function takes argument: opt.
    Calles function fn_urlopen, decodes the page, retrieves tickers.
    Returns a tuple of tickers.
    """
    global tickers
    tickers = []
    fn_urlopen(url)
    for tag in tags:
        tag = tag.decode()
        try:
            if opt == 1:
                sym = re.findall('>([A-Z]\S+[A-Z])</td>',tag)
            elif opt == 2:
                sym = re.findall('>(\S+=\S)</a>',tag)
            elif opt == 3:
                sym = re.findall('>(\S+-\S+)</a>',tag)
            tickers.append(sym[0])
        except: continue
    tickers = tuple(tickers)
    return tickers

# Select number of tickers to display
def fn_numtick(tickers):
    """
    Function takes argument: tickers.
    Prompts user for the number of tickers to display.
    Returns number of tickers to display.
    """
    global disp
    print('Number of tickers available: {}'.format(len(tickers)))
    while True:
        disp = input('Select number of tickers to display: ')
        try:
            if not disp.isdigit() or len(disp) < 1:
                disp = 4 ; break
            else:
                disp = int(disp) ; break
        except ValueError:
            print('Invalid number') ; continue
    return disp

# Create database
dbname = lst[opt-1] +'_'+ strftime('%Y%m')+'.sqlite'
conn = sqlite3.connect(dbname)
cur = conn.cursor()
print('\n*Accessing database %s' % (dbname))
cur.execute('''
            CREATE TABLE IF NOT EXISTS Tickers (
                id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                sym      TEXT UNIQUE
            )
            ''')
cur.execute('''
            CREATE TABLE IF NOT EXISTS Dates (
                id       INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                dt       TIMESTAMP UNIQUE
            )
            ''')
cur.execute('''
            CREATE TABLE IF NOT EXISTS Prices (
                ticker_id   INTEGER NOT NULL,
                dt_id       INTEGER NOT NULL,
                price       REAL
            )
            ''')
print('Database is valid and ready')

# insert tickers to database.Tickers
print('\n*Checking Tickers table in database')
for name in fn_tickers(opt):
    try:
        cur.execute('SELECT id FROM Tickers WHERE sym = ? ', (name, ))
        cur.fetchone()[0]
        print('%-10s | already exists in database' % name)
    except:
        cur.execute('''INSERT INTO Tickers (sym) VALUES ( ? )''', ( name, ) )
        print('%-10s | is added to database' % name)

# Prompt user for # of tickers to display
fn_numtick(tickers)

# Start mining cycles
good_count = 0 ; total_count = 0 ; avgt = 0 ; start_time = time()
print('\n-> Start mining data. Press "Ctrl+C" to stop.\n')

# display headers
def head():
    """
    Function takes no arguments.
    Displays headers.
    Returns none.
    """
    num = 0
    print(' '*8,end=' ')
    for i in tickers:
        if num < disp:
            print(' | {:^10s}'.format(i),end='')
            num += 1
    print()
head()

# setting up a timestamp
def fn_time():
    """
    Function takes no arguments.
    Records a timestamp when called.
    Returns none.
    """
    global st, now, bt
    st = strftime('%T')
    bt = time()
    now = datetime.today()
    pass

def fn_values(opt,tag):
    """
    Function takes arguments: opt, tag.
    Finds values using regular expressions.
    Returns raw.
    """
    global raw
    if opt == 1:
        raw = re.findall('>([0-9]\S+)</td>',tag)
    elif opt == 2:
        raw = re.findall('>([0-9,]+[.]+[0-9]+)</td>',tag)
    return raw

while True:
    try:
        # Define datetime objects
        fn_time()
        print(st, end=' ')

        # insert timestamp into database.Dates, return dt_id
        cur.execute('''INSERT OR IGNORE INTO Dates (dt)
                VALUES ( ? )''', ( now, ) )
        cur.execute('SELECT id FROM Dates WHERE dt = ? ', (now, ))
        dt_id = cur.fetchone()[0]

        # open url
        try:
            fn_urlopen(url)
            disp_count = 0
            ticker_id = 0
            # retrieve value
            for tag in tags:
                try:
                    tag = tag.decode()
                    fn_values(opt,tag)

                    # clean value
                    if len(raw)<1:
                        pass
                    elif '0.000000</span>' in raw:
                        pass
                    else:
                        val = float(raw[0].replace(',',''))

                        # insert value into Price.table
                        ticker_id += 1
                        try:
                            cur.execute('SELECT price FROM Prices WHERE (ticker_id, dt_id) = ( ?, ? ) ', ( ticker_id, dt_id ))
                            cur.fetchone()[0]
                        except:
                            cur.execute('INSERT INTO Prices (ticker_id, dt_id, price) VALUES ( ?, ?, ? )', ( ticker_id, dt_id, val ) )
                        # display values one-by-one
                        if disp_count < disp:
                            if opt == 1:
                                print(' | {:^10.3f}'.format(val), end='')
                            elif opt == 2:
                                print(' | {:^10.2f}'.format(val), end='')
                            elif opt == 3:
                                print(' | {:^10.4f}'.format(val), end='')
                            disp_count += 1
                        good_count += 1
                except Exception as exception_object:
                    print(" Decoding error: {0:}".format(exception_object))
                    pass
        except urllib.error.URLError: print(' URL timeout error') ; continue
        print()

        # record avg exec time, page refresh pause
        avgt += time()-bt
        sleep(lag)

    except KeyboardInterrupt:
        print('\nProgram interrupted by user')
        break
    except Exception as exception_object:
        print(" Unexpected error: {0:}".format(exception_object))
        continue
    finally:
        conn.commit()
        total_count += 1

        # intermediary report
        if total_count % 20 == 0:
            print('\nRetrieved %d units of data. Keep mining...' % good_count)
            print('Corrupt data: {:2.1f}%\n'.format(100-good_count/total_count/len(tickers)*100))
            head()

# Final statement
print('\nMining time: %.0f s' % (time() - start_time))
print('Average execution time: %.2f s' % (avgt/total_count))
print('Total data retrieved:',good_count,'units')
print('Corrupt data: {:2.1f}%'.format(100-good_count/total_count/len(tickers)*100))